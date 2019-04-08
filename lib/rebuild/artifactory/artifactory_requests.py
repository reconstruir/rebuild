#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import datetime, json, os.path as path, shutil, time
from collections import namedtuple

from bes.system import execute, log, os_env
from bes.common import check
from bes.fs import file_path, file_util, temp_file

from rebuild.base import requirement_list
from rebuild.package import package_metadata, package_metadata_list, package_manifest
from rebuild.storage.storage_address import storage_address

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
  
  _checksums = namedtuple('_checksums', 'md5, sha1, sha256')

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
    return clazz._checksums_from_headers(headers)

  @classmethod
  def _checksums_from_headers(clazz, headers):
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
    return clazz.download_url_to_file(target, address.url, username, password, debug = debug)

  @classmethod
  def download_url_to_file(clazz, target, url, username, password, debug = False):
    'Download file to target.'
    check.check_string(target)
    check.check_string(url)
    check.check_string(username)
    check.check_string(password)
    import requests
    tmp = temp_file.make_temp_file(suffix = '-' + path.basename(target), delete = not debug)
    auth = ( username, password )
    response = requests.get(url, auth = auth, stream = True)
    clazz.log_d('download_to_file: target=%s; url=%s; tmp=%s' % (target, url, tmp))
    if response.status_code != 200:
      return False
    with open(tmp, 'wb') as fout:
      shutil.copyfileobj(response.raw, fout)
      fout.close()
      file_util.copy(tmp, target)
      return True

  _file_item = namedtuple('_file_item', 'uri, filename, sha1')
  @classmethod
  def list_all_files(clazz, address, username, password):
    check.check_storage_address(address)
    check.check_string(username)
    check.check_string(password)
    url = artifactory_address.make_api_url(address, endpoint = 'storage', file_path = address.repo_filename, params = 'list&deep=1&listFolders=0')
    clazz.log_d('list_all_files:       address=%s' % (str(address)))
    clazz.log_d('list_all_files:           url=%s' % (url))
    clazz.log_d('list_all_files: repo_filename=%s' % (address.repo_filename))
    auth = ( username, password )
    import requests
    response = requests.get(url, auth = auth)
    # 404 means nothing has been ingested to the repo yet
    if response.status_code == 404:
      return []
    if response.status_code != 200:
      raise RuntimeError('failed to list_all_files for: %s (status_code %d)' % (url, response.status_code))
    data = response.json()
    #file_util.save('result.json', content = response.content)
    files = data.get('files', None)
    if not files:
      return []
    result = []
    for f in files:
      assert 'uri' in f
      assert 'sha1' in f
      filename = file_util.lstrip_sep(f['uri'])
      uri = str(address) + '/' + filename
      sha1 = file_util.lstrip_sep(f['sha1'])
      result.append(clazz._file_item(uri, filename, sha1))
    result.sort()
    return result

  @classmethod
  def upload(clazz, address, filename, username, password):
    check.check_storage_address(address)
    check.check_string(address.filename)
    check.check_string(username)
    check.check_string(password)
    clazz.log_d('upload: address=%s; filename=%s' % (address, filename))
    return clazz.upload_url(address.url, filename, username, password)

  @classmethod
  def upload_url(clazz, url, filename, username, password):
    check.check_string(url)
    check.check_string(username)
    check.check_string(password)
    clazz.log_d('upload_url: url=%s; filename=%s' % (url, filename))
    import requests
    headers = clazz.checksum_headers_for_file(filename)
    with open(filename, 'rb') as fin:
      response = requests.put(url,
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
  def delete_url(clazz, url, username, password):
    check.check_string(url)
    check.check_string(username)
    check.check_string(password)
    clazz.log_d('delete_url: url=%s' % (url))
    import requests
    response = requests.delete(url, auth = (username, password))
    clazz.log_d('delete: response status_code=%d' % (response.status_code))
    print('status_code: %s' % (response.status_code))
    print('   response: %s' % (response.json()))
#    if response.status_code != 201:
#      raise RuntimeError('Failed to upload: %s (status_code %d)' % (url, response.status_code))
#      data = response.json()
#      assert 'downloadUri' in data
#      return data['downloadUri']
    return None
    
  @classmethod
  def checksum_headers_for_file(clazz, filename):
    return {
      clazz._HEADER_CHECKSUM_MD5: file_util.checksum('md5', filename),
      clazz._HEADER_CHECKSUM_SHA1: file_util.checksum('sha1', filename),
      clazz._HEADER_CHECKSUM_SHA256: file_util.checksum('sha256', filename),
    }
    
  @classmethod
  def set_properties(clazz, address, properties, username, password):
    check.check_storage_address(address)
    check.check_string(username)
    check.check_string(password)
    check.check_dict(properties)

    import requests
    url = artifactory_address.make_api_url(address, endpoint = 'metadata', file_path = address.file_path)
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

    print('ADDRESS: %s' % (str(address._asdict())))
    
    # an artifactory AQL query to find all the artifacts in a repo
    template = '''
items.find({{
  "repo":"{repo}",
  "path" : {{"$match":"{match_prefix}/*"}}
}}).include("*", "property.*")
'''
    match_prefix = '{root_dir}/{sub_repo}'.format(root_dir = address.root_dir, sub_repo = address.sub_repo)
    match_prefix = address.repo_filename
    match_prefix = 'ego-devenv-v2/artifacts/macos-10/x86_64/release'
    print('ADDRESS: %s' % (str(address._asdict())))
    print('repo_filename=%s' % (address.repo_filename))
    aql = template.format(repo = address.repo,  match_prefix = match_prefix)

    clazz.log_d('list_all_artifacts: aql=%s' % (aql), multi_line = True)

    url = artifactory_address.make_search_aql_url(address)
    clazz.log_d('list_all_artifacts: url=%s' % (url))
    auth = ( username, password )
    import requests
    print('url=%s' % (url))
    print('aql=%s' % (aql))
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
    distro_version_major = None
    distro_version_minor = None
    requirements = []
    properties = {}
    files = package_manifest(None, None)

    for artifactory_prop in artifactory_properties:
      if artifactory_prop['key'] == 'rebuild.distro_version_major':
        distro_version_major = artifactory_prop.get('value', '')
      elif artifactory_prop['key'] == 'rebuild.distro_version_minor':
        distro_version_minor = artifactory_prop.get('value', '')
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
        distro = artifactory_prop.get('value', '')
      elif artifactory_prop['key'] == 'rebuild.requirements':
        requirements.append(artifactory_prop['value'])

    requirements = requirement_list.from_string_list(requirements)
         
    return package_metadata(package_metadata.FORMAT_VERSION, filename, name,
                            version, revision, epoch, system, level, arch, distro,
                            distro_version_major or '',  distro_version_minor or '',
                            requirements, properties, files)

  _file_info = namedtuple('_file_info', 'filename, content_length, content_type, date, etag, last_modified, md5, sha1, sha256')
  @classmethod
  def get_info_file_url(clazz, url, username, password):
    'Return info for the given file url or None if it is not a file.'
    check.check_string(url)
    check.check_string(username)
    check.check_string(password)
    headers = clazz.get_headers_for_url(url, username, password)
    if not headers:
      return None
    checksums = clazz._checksums_from_headers(headers)
    return clazz._file_info(headers['X-Artifactory-Filename'],
                            headers['Content-Length'],
                            headers['Content-Type'],
                            headers.get('Date', None),
                            headers.get('ETag', None),
                            headers.get('Last-Modified', None),
                            checksums.md5,
                            checksums.sha1,
                            checksums.sha256)

  _file_stats = namedtuple('_file_stats', 'uri, download_count, last_downloaded, last_downloaded_by, remote_download_count, remote_last_downloaded')
  @classmethod
  def get_file_stats(clazz, url, username, password):
    'Return download stats for the given artifactory url.'
    check.check_string(url)
    check.check_string(username)
    check.check_string(password)
    auth = ( username, password )
    import requests
    address = storage_address.parse_url(url, has_host_root = True)
    url = artifactory_address.make_api_url(address, endpoint = 'storage', file_path = address.repo_filename, params = 'stats')
    response = requests.get(url, auth = auth)
    # 404 means nothing has been ingested to the repo yet
    if response.status_code == 404:
      return []
    if response.status_code != 200:
      raise RuntimeError('failed to get stats: %s (status_code %d)' % (url, response.status_code))
    data = response.json()
    uri = data.get('uri', None)
    if not uri:
      raise RuntimeError('malformed response for url: {} - {}' % (url, str(data)))
    uri = data.get('uri', None)
    download_count = data.get('downloadCount', None)
    last_downloaded = clazz._epoch_timestamp_to_datetime(data.get('lastDownloaded', None))
    last_downloaded_by = data.get('lastDownloadedBy', None)
    remote_download_count = data.get('remoteDownloadCount', None)
    remote_last_downloaded = clazz._epoch_timestamp_to_datetime(data.get('remoteLastDownloaded', None))
    return clazz._file_stats(uri, download_count, last_downloaded, last_downloaded_by, remote_download_count, remote_last_downloaded)

  @classmethod
  def _epoch_timestamp_to_datetime(clazz, t):
    'Convert an epoch timestamp in milliseconds to a datetime object.'
    if not t:
      return None
    t_seconds = t / 1000.0
    return datetime.datetime.strptime(time.ctime(t_seconds), '%a %b %d %H:%M:%S %Y')
  
log.add_logging(artifactory_requests, 'artifactory_requests')
