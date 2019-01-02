#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path, shutil
from collections import namedtuple

from bes.system import execute, log, os_env
from bes.common import check
from bes.fs import file_path, file_util, temp_file

from rebuild.base import requirement_list
from rebuild.package import package_metadata, package_metadata_list, package_manifest

from .artifactory_address import artifactory_address

class artifactory_requests(object):

  @classmethod
  def get_headers(clazz, address, username, password):
    check.check_storage_address(address)
    check.check_string(address.filename)
    check.check_string(username)
    check.check_string(password)
    return clazz.get_headers_for_url(address.url, username, password)

  @classmethod
  def get_headers_for_url(clazz, url, username, password):
    check.check_string(url)
    check.check_string(username)
    check.check_string(password)
    import requests
    auth = ( username, password )
    clazz.log_d('get_headers_for_url: url=%s' % (url))
    response = requests.head(url, auth = auth)
    clazz.log_d('get_headers_for_url: status_code=%s; headers=%s' % (response.status_code, response.headers))
    if response.status_code != 200:
      return None
    return response.headers
  
  _checksums = namedtuple('namedtuple', 'md5, sha1, sha256')

  _HEADER_CHECKSUM_MD5 = 'X-Checksum-Md5'
  _HEADER_CHECKSUM_SHA1 = 'X-Checksum-Sha1'
  _HEADER_CHECKSUM_SHA256 = 'X-Checksum-Sha256'

  @classmethod
  def get_checksums_for_url(clazz, url, username, password):
    check.check_string(url)
    check.check_string(username)
    check.check_string(password)
    clazz.log_d('get_checksums_for_url: url=%s' % (url))
    headers = clazz.get_headers_for_url(url, username, password)
    clazz.log_d('get_checksums_for_url: headers=%s' % (headers))
    if not headers:
      return None
    md5 = headers.get(clazz._HEADER_CHECKSUM_MD5, None)
    sha1 = headers.get(clazz._HEADER_CHECKSUM_SHA1, None)
    sha256 = headers.get(clazz._HEADER_CHECKSUM_SHA256, None)
    return clazz._checksums(md5, sha1, sha256)
  
  @classmethod
  def get_checksums(clazz, address, username, password):
    check.check_storage_address(address)
    check.check_string(address.filename)
    check.check_string(username)
    check.check_string(password)
    return clazz.get_checksums_for_url(address.url, username, password)

  @classmethod
  def download_to_file(clazz, target, address, username, password, debug = False):
    'Download file to target.'
    check.check_string(target)
    check.check_storage_address(address)
    check.check_string(address.filename)
    check.check_string(username)
    check.check_string(password)
    import requests
    tmp = temp_file.make_temp_file(suffix = '-' + path.basename(target), delete = not debug)
    auth = ( username, password )
    response = requests.get(address.url, auth = auth, stream = True)
    clazz.log_d('download_to_file: target=%s; address=%s; tmp=%s' % (target, address, tmp))
    if response.status_code != 200:
      return False
    with open(tmp, 'wb') as fout:
      shutil.copyfileobj(response.raw, fout)
      fout.close()
      file_util.copy(tmp, target)
      return True

  @classmethod
  def list_all_files(clazz, address, username, password):
    check.check_storage_address(address)
    check.check_string(username)
    check.check_string(password)
    url = artifactory_address.make_api_url(address, endpoint = 'storage', file_path = address.file_folder, params = 'list&deep=1&listFolders=0')
    clazz.log_d('list_all_files: address=%s; url=%s' % (address, url))
    auth = ( username, password )
    import requests
    response = requests.get(url, auth = auth)
    clazz.log_d('list_all_files: response status_code=%d' % (response.status_code))
    # 404 means nothing has been ingested to the repo yet
    if response.status_code == 404:
      return []
    if response.status_code != 200:
      raise RuntimeError('failed to list_all_files for: %s (status_code %d)' % (url, response.status_code))
    data = response.json()
    files = data.get('files', None)
    if not files:
      return []
    result = []
    for f in files:
      assert 'uri' in f
      assert 'sha1' in f
      filename = file_util.lstrip_sep(f['uri'])
      sha1_checksum = file_util.lstrip_sep(f['sha1'])
      result.append( ( filename, sha1_checksum ) )
    result.sort()
    return result

  @classmethod
  def upload(clazz, address, filename, username, password):
    check.check_storage_address(address)
    check.check_string(address.filename)
    check.check_string(username)
    check.check_string(password)
    clazz.log_d('upload: address=%s; filename=%s' % (address, filename))
    import requests
    headers = {
      # 'content-type': content_type,
      clazz._HEADER_CHECKSUM_MD5: file_util.checksum('md5', filename),
      clazz._HEADER_CHECKSUM_SHA1: file_util.checksum('sha1', filename),
      clazz._HEADER_CHECKSUM_SHA256: file_util.checksum('sha256', filename),
    }
    with open(filename, 'rb') as fin:
      response = requests.put(address.url,
                              auth = (username, password),
                              data = fin,
                              headers = headers)
      clazz.log_d('upload: response status_code=%d' % (response.status_code))
      if response.status_code != 201:
        raise RuntimeError('Failed to upload: %s (status_code %d)' % (url, response.status_code))
      data = response.json()
      assert 'downloadUri' in data
      return data['downloadUri']

  @classmethod
  def set_properties(clazz, address, properties, username, password):
    check.check_storage_address(address)
    check.check_string(username)
    check.check_string(password)
    check.check_dict(properties)

    import requests

    url = address.make_api_url(endpoint = 'metadata', file_path = address.file_path)
    clazz.log_d('set_properties: address=%s; url=%s' % (address, url))
    
    # In order to patch properties artifactory expects dict with 'props'
    json_data = { 'props': properties }
    
    auth = ( username, password )
    clazz.log_d('set_properties: url=%s; username=%s; password=%s' % (url, username, password))
    response = requests.patch(url, json = json_data, auth = auth)
    clazz.log_d('set_properties: response: %s' % (str(response)))
    if response.status_code != 204:
      clazz.log_e('set_properties: failed to set properties: %s' % (url))
      return False
    return True

  @classmethod
  def list_all_artifacts(clazz, address, username, password):
    check.check_storage_address(address)
    clazz.log_d('list_all_artifacts: address=%s' % (str(address)))

    # an artifactory AQL query to find all the artifacts in a repo
    template = '''
items.find({
  "repo":"%s",
  "path" : {"$match":"%s/*"}
}).include("*", "property.*")
'''
    match_prefix = '{root_dir}/{sub_repo}'.format(root_dir = address.root_dir, sub_repo = address.sub_repo)
    aql = template % (address.repo, match_prefix)

    clazz.log_d('list_all_artifacts: aql=%s' % (aql), multi_line = True)

    url = artifactory_address.make_search_aql_url(address)
    print('CACA: url=%s' % (url))
    clazz.log_d('list_all_artifacts: url=%s' % (url))
    auth = ( username, password )
    import requests
    response = requests.post(url, data = aql, auth = auth)
    clazz.log_d('list_all_artifacts: response=%s; status_code=%d' % (str(response), response.status_code))
    if response.status_code != 200:
      raise RuntimeError('failed to list_all_artifacts for: %s (status_code %d)' % (url, response.status_code))
    data = response.json()
    assert 'results' in data
    results = data['results']
    result = package_metadata_list()
    for item in results:
      assert 'path' in item
      item_name = item.get('name', None)
      item_path = item.get('path', None)
      filename = path.join(file_util.remove_head(item_path, match_prefix), item_name)
      #print('CACA: item_name=%s; item_path=%s; filename=%s' % (item_name, item_path, filename))
      item_properties = item.get('properties', None)
      if item_properties:
        md = clazz._parse_artifact_properties(filename, item_properties)
        result.append(md)
      else:
        clazz.log_e('artifact missing properties: %s - %s - %s' % (address, item_path, item_name))
    return result
  
  @classmethod
  def _parse_artifact_properties(clazz, filename, artifactory_properties):
    # FIXME: properties missing from artifactory rebuild.* properties
    name = None
    version = None
    revision = None
    epoch = None
    system = None
    level = None
    arch = None
    distro = None
    distro_version = None
    requirements = []
    properties = {}
    files = package_manifest(None, None)
    
    for artifactory_prop in artifactory_properties:
      if artifactory_prop['key'] == 'rebuild.distro_version':
        distro_version = artifactory_prop['value']
      elif artifactory_prop['key'] == 'rebuild.name':
        name = artifactory_prop['value']
      elif artifactory_prop['key'] == 'rebuild.version':
        version = artifactory_prop['value']
      elif artifactory_prop['key'] == 'rebuild.revision':
        revision = artifactory_prop['value']
      elif artifactory_prop['key'] == 'rebuild.epoch':
        epoch = artifactory_prop['value']
      elif artifactory_prop['key'] == 'rebuild.system':
        system = artifactory_prop['value']
      elif artifactory_prop['key'] == 'rebuild.level':
        level = artifactory_prop['value']
      elif artifactory_prop['key'] == 'rebuild.arch':
        arch = artifactory_prop['value']
      elif artifactory_prop['key'] == 'rebuild.distro':
        distro = artifactory_prop['value']
      elif artifactory_prop['key'] == 'rebuild.requirements':
        requirements.append(artifactory_prop['value'])

    requirements = requirement_list.from_string_list(requirements)
         
    return package_metadata(filename, name, version, revision, epoch, system,
                            level, arch, distro, distro_version, requirements,
                            properties, files)
  
log.add_logging(artifactory_requests, 'artifactory_requests')
