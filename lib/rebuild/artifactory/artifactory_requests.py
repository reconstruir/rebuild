  #-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import datetime, json, os.path as path, shutil, time
from collections import namedtuple

from bes.system.execute import execute
from bes.system.log import log
from bes.system.os_env import os_env
from bes.common.check import check
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from rebuild.base import requirement_list
from rebuild.package import package_metadata, package_metadata_list, package_manifest
from rebuild.storage.storage_address import storage_address
from rebuild.credentials.credentials import credentials

from .artifactory_address import artifactory_address

class artifactory_error(Exception):

  def __init__(self, message, status_code, content):
    super(artifactory_error, self).__init__(message)
    self.message = message
    self.status_code = status_code
    self.content = content

class artifactory_requests(object):

  @classmethod
  def get_headers(clazz, address, credentials):
    check.check_storage_address(address)
    check.check_string(address.filename)
    check.check_credentials(credentials)
    return clazz.get_headers_for_url(address.url, credentials)

  @classmethod
  def get_headers_for_url(clazz, url, credentials):
    check.check_string(url)
    check.check_credentials(credentials)
    import requests
    auth = ( credentials.username, credentials.password )
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
  def get_checksums_for_url(clazz, url, credentials):
    check.check_string(url)
    check.check_credentials(credentials)
    clazz.log_d('get_checksums_for_url: url=%s' % (url))
    headers = clazz.get_headers_for_url(url, credentials)
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
  def get_checksums(clazz, address, credentials):
    check.check_storage_address(address)
    check.check_string(address.filename)
    check.check_credentials(credentials)
    return clazz.get_checksums_for_url(address.url, credentials)

  @classmethod
  def download_to_file(clazz, target, address, credentials, debug = False):
    'Download file to target.'
    return clazz.download_url_to_file(target, address.url, credentials, debug = debug)

  @classmethod
  def download_url_to_file(clazz, target, url, credentials, debug = False, checksum = True):
    'Download file to target.'
    check.check_string(target)
    check.check_string(url)
    check.check_credentials(credentials)
    check.check_bool(debug)
    check.check_bool(checksum)

    import requests
    tmp = temp_file.make_temp_file(suffix = '-' + path.basename(target), delete = not debug)
    auth = ( credentials.username, credentials.password )
    response = requests.get(url, auth = auth, stream = True)
    clazz.log_d('download_to_file: target=%s; url=%s; tmp=%s' % (target, url, tmp))
    if response.status_code != 200:
      return False
    with open(tmp, 'wb') as fout:
      shutil.copyfileobj(response.raw, fout)
      fout.close()
      if checksum:
        checksums = clazz.get_checksums_for_url(url, credentials)
        expected_checksum = checksums.sha256
        actual_checksum = file_util.checksum('sha256', tmp)
        if expected_checksum != actual_checksum:
          msg = 'Checksum for download does not match expected: {}'.format(url)
          raise artifactory_error(msg, None, None)
      file_util.copy(tmp, target)
      return True

  _file_item = namedtuple('_file_item', 'uri, filename, sha1')
  @classmethod
  def list_files(clazz, address, credentials):
    check.check_storage_address(address)
    check.check_credentials(credentials)
    url = artifactory_address.make_api_url(address, endpoint = 'storage', file_path = address.repo_filename, params = 'list&deep=1&listFolders=0')
    clazz.log_d('list_files:       address=%s' % (str(address)))
    clazz.log_d('list_files:           url=%s' % (url))
    clazz.log_d('list_files: repo_filename=%s' % (address.repo_filename))
    auth = ( credentials.username, credentials.password )
    import requests
    response = requests.get(url, auth = auth)
    # 404 means nothing has been ingested to the repo yet
    if response.status_code == 404:
      return []
    if response.status_code != 200:
      msg = 'failed to list_files for: {} (status_code {})'.format(url, response.status_code)
      raise artifactory_error(msg, response.status_code, response.content)
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
  def upload(clazz, address, filename, credentials, num_tries = 1):
    check.check_storage_address(address)
    check.check_string(address.filename)
    check.check_credentials(credentials)
    clazz.log_d('upload: address=%s; filename=%s' % (address, filename))
    return clazz.upload_url(address.url, filename, credentials)

  @classmethod
  def upload_url(clazz, url, filename, credentials, num_tries = 1):
    check.check_string(url)
    check.check_credentials(credentials)
    clazz.log_d('upload_url: url=%s; filename=%s' % (url, filename))

    if num_tries < 1 or num_tries > 10:
      raise ValueError('num_tries should be between 1 and 10')

    last_ex = None
    for i in range(1, num_tries + 1):
      clazz.log_d('upload_url: attempt {} of {} for {}'.format(i, num_tries, url))
      try:
        download_url = clazz._do_upload_url(url, filename, credentials)
        clazz.log_d('upload_url: SUCCESS: attempt {} of {} for {} download_url={}'.format(i, num_tries, url, download_url))
        return download_url
      except artifactory_error as ex:
        clazz.log_e('upload_url: FAILED: attempt {} of {} for {}'.format(i, num_tries, url))
        last_ex = ex
        
    raise last_ex
    
  @classmethod
  def _do_upload_url(clazz, url, filename, credentials):
    clazz.log_d('_do_upload_url: url=%s; filename=%s' % (url, filename))
    import requests
    headers = clazz.checksum_headers_for_file(filename)

    '''
    old_checksums = clazz.get_checksums_for_url(url, credentials)
    if old_checksums:
      new_sha256 = headers[clazz._HEADER_CHECKSUM_SHA256]
      if old_checksums.sha256 == new_sha256:
        clazz.log_i('_do_upload_url: url exists with same checksum.  doing nothing: {}'.format(url))
        return url
      msg = 'Trying to re-upload artifact with different checksum:\nfilename={}\nurl={}'.format(filename, url)
      raise artifactory_error(msg, None, None)
'''
    
    with open(filename, 'rb') as fin:
      response = requests.put(url,
                              auth = ( credentials.username, credentials.password ),
                              data = fin,
                              headers = headers)
      clazz.log_d('_do_upload_url: response status_code=%d' % (response.status_code))
      if response.status_code != 201:
        msg = 'Failed to upload: {} (status_code {} content {})'.format(url, response.status_code, response.content)
        raise artifactory_error(msg, response.status_code, response.content)
      data = response.json()
      assert 'downloadUri' in data
      return data['downloadUri']
    
  _delete_result = namedtuple('_delete_result', 'success, status_code')
  @classmethod
  def delete_url(clazz, url, raise_error, credentials):
    check.check_string(url)
    check.check_credentials(credentials)
    clazz.log_d('delete_url: url=%s' % (url))
    import requests
    response = requests.delete(url, auth = (credentials.username, credentials.password))
    clazz.log_d('delete: response status_code=%d' % (response.status_code))
    success = response.status_code == 204
    if not success and raise_error:
      msg = 'Failed to delete: {} (status_code {})'.format(url, response.status_code)
      raise artifactory_error(msg, response.status_code, response.content)
    return clazz._delete_result(success, response.status_code)
    
  @classmethod
  def checksum_headers_for_file(clazz, filename):
    return {
      clazz._HEADER_CHECKSUM_MD5: file_util.checksum('md5', filename),
      clazz._HEADER_CHECKSUM_SHA1: file_util.checksum('sha1', filename),
      clazz._HEADER_CHECKSUM_SHA256: file_util.checksum('sha256', filename),
    }
    
  @classmethod
  def set_properties(clazz, address, properties, credentials):
    check.check_storage_address(address)
    check.check_credentials(credentials)
    check.check_dict(properties)

    import requests
    url = artifactory_address.make_api_url(address, endpoint = 'metadata', file_path = address.repo_filename)
    clazz.log_d('set_properties: address=%s; url=%s' % (address, url))
    
    # In order to patch properties artifactory expects dict with 'props'
    json_data = { 'props': properties }
    
    auth = ( credentials.username, credentials.password )
    clazz.log_d('set_properties: url={}; credentials={}'.format(url, credentials))
    response = requests.patch(url, json = json_data, auth = auth)
    clazz.log_d('set_properties: response: %s' % (str(response)))
    if response.status_code != 204:
      clazz.log_e('set_properties: failed to set properties: %s' % (url))
      return False
    return True

  @classmethod
  def list_artifacts(clazz, address, credentials):
    'List artifacts in an artifactory directory.'
    check.check_storage_address(address)
    clazz.log_d('list_artifacts: address=%s' % (str(address)))
    # an artifactory AQL query to find all the artifacts in a repo
    template = '''
items.find({{
  "repo":"{repo}",
  "path" : {{"$match":"{match_prefix}*"}}
}}).include("*", "property.*")
'''
    match_prefix = file_util.remove_head(address.repo_filename, address.repo)
    aql = template.format(repo = address.repo,  match_prefix = match_prefix)
    clazz.log_d('list_artifacts: address={}'.format(address))
    clazz.log_d('list_artifacts: match_prefix={}'.format(match_prefix))
    clazz.log_d('list_artifacts: aql=%s' % (aql), multi_line = True)

    aql_url = artifactory_address.make_search_aql_url(address)
    clazz.log_d('list_artifacts: aql_url=%s' % (aql_url))
    auth = ( credentials.username, credentials.password )
    import requests
    response = requests.post(aql_url, data = aql, auth = auth)
    clazz.log_d('list_artifacts: response=%s; status_code=%d' % (str(response), response.status_code))
    if response.status_code != 200:
      msg = 'failed to list_artifacts for: {} (status_code {})'.format(aql_url, response.status_code)
      raise artifactory_error(msg, response.status_code, response.content)
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
  def get_file_info_url(clazz, url, credentials):
    'Return info for the given file url or None if it is not a file.'
    check.check_string(url)
    check.check_credentials(credentials)
    headers = clazz.get_headers_for_url(url, credentials)
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
  def get_file_stats(clazz, url, credentials):
    'Return download stats for the given artifactory url.'
    check.check_string(url)
    check.check_credentials(credentials)
    auth = ( credentials.username, credentials.password )
    import requests
    address = storage_address.parse_url(url, has_host_root = True)
    api_url = artifactory_address.make_api_url(address, endpoint = 'storage', file_path = address.repo_filename, params = 'stats')
    response = requests.get(api_url, auth = auth)
    if response.status_code != 200:
      msg = 'failed to get stats: {} (status_code {})'.format(api_url, response.status_code)
      raise artifactory_error(msg, response.status_code, response.content)
    data = response.json()
    uri = data.get('uri', None)
    if not uri:
      msg = 'malformed response for api_url: {} - {}'.format(api_url, str(data))
      raise artifactory_error(msg, response.status_code, response.content)
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

  @classmethod
  def get_file_properties_url(clazz, url, credentials):
    'Return info for the given file url or None if it is not a file.'
    check.check_string(url)
    check.check_credentials(credentials)
    auth = ( credentials.username, credentials.password )
    import requests
    address = storage_address.parse_url(url, has_host_root = True)
    api_url = artifactory_address.make_api_url(address, endpoint = 'storage', file_path = address.repo_filename, params = 'properties')
    response = requests.get(api_url, auth = auth)
    if response.status_code != 200:
      msg = 'failed to get properties: {} (status_code {})'.format(api_url, response.status_code)
      raise artifactory_error(msg, response.status_code, response.content)
    data = response.json()
    properties = data.get('properties', None)
    if not properties:
      msg = 'malformed response for api_url: {} - {}'.format(api_url, str(data))
      raise artifactory_error(msg, response.status_code, response.content)
    return properties
  
log.add_logging(artifactory_requests, 'artifactory_requests')
