#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path, shutil
from collections import namedtuple

from bes.system import execute, log, os_env
from bes.common import check
from bes.fs import file_path, file_util, temp_file

class artifactory_requests(object):

  @classmethod
  def fetch_headers(clazz, url, username, password):
    check.check_string(url)
    check.check_string(username)
    check.check_string(password)
    import requests
    auth = ( username, password )
    clazz.log_d('fetch_headers: url=%s; username=%s; password=%s' % (url, username, password))
    response = requests.head(url, auth = auth)
    clazz.log_d('fetch_headers: status_code=%s; headers=%s' % (response.status_code, response.headers))
    if response.status_code != 200:
      return None
    return response.headers

  _checksums = namedtuple('namedtuple', 'md5, sha1, sha256')

  _HEADER_CHECKSUM_MD5 = 'X-Checksum-Md5'
  _HEADER_CHECKSUM_SHA1 = 'X-Checksum-Sha1'
  _HEADER_CHECKSUM_SHA256 = 'X-Checksum-Sha256'
  
  @classmethod
  def fetch_checksums(clazz, url, username, password):
    check.check_string(url)
    check.check_string(username)
    check.check_string(password)

    headers = clazz.fetch_headers(url, username, password)
    clazz.log_d('fetch_checksums: headers=%s' % (headers))
    if not headers:
      return None

    md5 = headers.get(clazz._HEADER_CHECKSUM_MD5, None)
    sha1 = headers.get(clazz._HEADER_CHECKSUM_SHA1, None)
    sha256 = headers.get(clazz._HEADER_CHECKSUM_SHA256, None)
    return clazz._checksums(md5, sha1, sha256)

  @classmethod
  def download_to_file(clazz, target, url, username, password):
    'Download file to target.'
    import requests
    tmp = temp_file.make_temp_file(suffix = '-' + path.basename(target), delete = False)
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

  @classmethod
  def list_all_files(clazz, hostname, root_dir, repo, username, password):
    clazz.log_d('list_all_files: hostname=%s; root_dir=%s; repo=%s' % (hostname, root_dir, repo))
    if hostname.endswith('/'):
      hostname = hostname[0:-1]
    root_dir = file_util.strip_sep(root_dir)
    template = '{hostname}/api/storage/{root_dir}/{repo}?list&deep=1&listFolders=0'
    url = template.format(hostname = hostname, root_dir = root_dir, repo = repo)
    clazz.log_d('list_all_files: url=%s' % (url))
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
  def upload(clazz, url, filename, username, password):
    #content_type = 'application/java-archive' # your content-type header
    import requests
    headers = {
      # 'content-type': content_type,
      clazz._HEADER_CHECKSUM_MD5: file_util.checksum('md5', filename),
      clazz._HEADER_CHECKSUM_SHA1: file_util.checksum('sha1', filename),
      clazz._HEADER_CHECKSUM_SHA256: file_util.checksum('sha256', filename),
    }
    with open(filename, 'rb') as f:
      response = requests.put(url,
                              auth = (username, password),
                              data = f,
                              headers = headers)
      if response.status_code != 201:
        raise RuntimeError('Failed to upload: %s (status_code %d)' % (url, response.status_code))
      data = response.json()
      assert 'downloadUri' in data
      return data['downloadUri']

  @classmethod
  def set_properties(clazz, hostname, root_dir, repo, filename, username, password, properties):
    check.check_string(hostname)
    check.check_string(root_dir)
    check.check_string(repo)
    check.check_string(username)
    check.check_string(password)
    check.check_dict(properties)

    import requests

    template = '{hostname}/api/metadata/{root_dir}/{repo}/{filename}'
    url = template.format(hostname = hostname, root_dir = root_dir, repo = repo, filename = filename)

    json_data = { 'props': properties }
    
    auth = ( username, password )
    clazz.log_d('set_properties: url=%s; username=%s; password=%s' % (url, username, password))
    response = requests.patch(url, json = json_data, auth = auth)
    clazz.log_d('set_properties: response: %s' % (str(response)))
    if response.status_code != 204:
      clazz.log_e('set_properties: failed to set properties: %s' % (url))
      return False
    return True
  
log.add_logging(artifactory_requests, 'artifactory_requests')
