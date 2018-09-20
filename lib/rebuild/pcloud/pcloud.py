#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib, os.path as path, requests, urlparse
from bes.common import check

from .pcloud_error import pcloud_error
from .pcloud_metadata import pcloud_metadata

class pcloud(object):

  API = 'https://api.pcloud.com'
  
  def __init__(self, email, password):
    digest = self._get_digest()
    password_digest = self._make_password_digest(digest, email, password)
    self._auth_token = self._get_auth_token(digest, email, password_digest)
    del email
    del password

  def list_folder(self, folder_path = None, folder_id = None, recursive = False, checksums = False):
    if not folder_path and not folder_id:
      raise ValueError('Etiher folder_path or folder_id should be given.')
    elif folder_path and folder_id:
      raise ValueError('Only one of folder_path or folder_id should be given.')
    url = self._make_api_url('listfolder')
    params = {
      'auth': self._auth_token,
      'recursive': int(recursive),
    }
    what = ''
    if folder_path:
      what = folder_path
      params.update({ 'path': folder_path })
    if folder_id:
      what = folder_id
      params.update({ 'folderid': folder_id })
    response = requests.get(url, params = params)
    payload = response.json()
    assert 'result' in payload
    if payload['result'] != 0:
      raise pcloud_error(payload['result'], what)
    assert 'metadata' in payload
    folder_metadata = payload['metadata']
    assert 'contents' in folder_metadata
    contents = folder_metadata['contents']
    result = [ pcloud_metadata.parse_dict(item) for item in contents ]
    if checksums:
      result = self._get_checksums(result)
    return result

  def delete_file(self, file_path = None, file_id = None):
    if not file_path and not file_id:
      raise ValueError('Etiher file_path or file_id should be given.')
    elif file_path and file_id:
      raise ValueError('Only one of file_path or file_id should be given.')
    url = self._make_api_url('deletefile')
    params = {
      'auth': self._auth_token,
    }
    what = ''
    if file_path:
      what = file_path
      params.update({ 'path': file_path })
    if file_id:
      what = file_id
      params.update({ 'fileid': file_id })
    response = requests.get(url, params = params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.json()
    assert 'result' in payload
    if payload['result'] != 0:
      raise pcloud_error(payload['result'], what)
    assert 'metadata' in payload
    return payload['metadata']
  
  def create_folder(self, folder_id = None, folder_name = None, folder_path = None):
    if folder_path:
      if folder_id:
        raise ValueError('Only one of folder_path or folder_id can be given.')
      if folder_name:
        raise ValueError('Only one of folder_path or folder_name can be given.')
    else:
      if not folder_id:
        raise ValueError('folder_id must be valid.')
      if not folder_name:
        raise ValueError('folder_name must be valid.')
    url = self._make_api_url('createfolder')
    params = {
      'auth': self._auth_token,
    }
    what = ''
    if folder_path:
      params.update({ 'path': folder_path })
      what = folder_path
    else:
      params.update({ 'folderid': folder_id })
      params.update({ 'name': folder_name })
      what = '%s - %s' % (folderid, name)
    response = requests.get(url, params = params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.json()
    assert 'result' in payload
    if payload['result'] != 0:
      raise pcloud_error(payload['result'], what)
    assert 'metadata' in payload
    return payload['metadata']
    
  def delete_folder(self, folder_id = None, folder_path = None):
    if not folder_path and not folder_id:
      raise ValueError('Etiher folder_path or folder_id should be given.')
    elif folder_path and folder_id:
      raise ValueError('Only one of folder_path or folder_id should be given.')
          
    url = self._make_api_url('deletefolder')
    params = {
      'auth': self._auth_token,
    }
    what = ''
    if folder_path:
      params.update({ 'path': folder_path })
      what = folder_path
    else:
      params.update({ 'folderid': folder_id })
      what = folderid
    response = requests.get(url, params = params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.json()
    print(payload)
    if 'metadata' in payload:
      return payload['metadata']
    raise pcloud_error(payload['result'], what)
  
  def _get_checksums(self, contents):
    return [ self._get_checksum(item) for item in contents ]
  
  def _get_checksum(self, item):
    check.check_pcloud_metadata(item)
    if item.is_folder:
      new_contents = [ self._get_checksum(child_item) for child_item in item.contents or [] ]
      new_item = item.mutate_contents(new_contents)
    else:
      checksum = self.checksum_file(file_id = item.pcloud_id)
      new_item = item.mutate_checksum(checksum)
    return new_item
    
  def checksum_file(self, file_path = None, file_id = None):
    if not file_path and not file_id:
      raise ValueError('Etiher file_path or file_id should be given.')
    elif file_path and file_id:
      raise ValueError('Only one of file_path or file_id should be given.')
    url = self._make_api_url('checksumfile')
    params = {
      'auth': self._auth_token,
    }
    what = ''
    if file_path:
      what = file_path
      params.update({ 'path': file_path })
    if file_id:
      what = file_id
      params.update({ 'fileid': file_id })
    response = requests.get(url, params = params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.json()
    assert 'result' in payload
    if payload['result'] != 0:
      raise pcloud_error(payload['result'], what)
    assert 'sha1' in payload
    return payload['sha1']

  def upload_file(self, local_path, cloud_filename, folder_path = None, folder_id = None):
    if not path.isfile(local_path):
      raise IoError('File not found: %s' % (local_path))
    if not folder_path and not folder_id:
      raise ValueError('Etiher folder_path or folder_id should be given.')
    elif folder_path and folder_id:
      raise ValueError('Only one of folder_path or folder_id should be given.')
    if path.isabs(cloud_filename):
      raise ValueError('cloud_filename should be just a filename: %s' % (cloud_filename))

    try:
      self.list_folder(folder_path = folder_path, folder_id = folder_id)
    except pcloud_error as ex:
      print('need to create dir for: %s - %s' % (folder_path, folder_id))
      assert False
    
#    try:
#      cloud_checksum = self.checksum_file(file_path = cloud_path)
#    except error as ex:
#      if ex.code == error.PARENT_DIR_MISSING:
#        print('need to create dir for %s' % (cloud_path))
#        assert False
    
    files = { cloud_filename: open(local_path, 'rb') }
    url = self._make_api_url('uploadfile')
    params = {
      'auth': self._auth_token,
      'filename': cloud_filename,
    }
    what = ''
    if folder_path:
      what = folder_path
      params.update({ 'path': folder_path })
    if folder_id:
      what = folder_id
      params.update({ 'folderid': folder_id })
    response  = requests.post(url, data = params, files = files)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.json()
    assert 'result' in payload
    if payload['result'] != 0:
      raise pcloud_error(payload['result'], what)
    assert 'metadata' in payload
    return payload['metadata']
  
  @classmethod
  def _make_password_digest(clazz, digest, email, password):
    'Make a password digest.'
    email_digest = hashlib.sha1(email.lower()).hexdigest()
    password_digest_input = password + email_digest + digest
    return hashlib.sha1(password + email_digest + digest).hexdigest()

  @classmethod
  def _get_digest(clazz):
    'Get a digest from pcloud to use with subsequent api calls.'
    url = clazz._make_api_url('getdigest')
    response = requests.get(url)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.json()
    assert 'digest' in payload
    return payload['digest']

  @classmethod
  def _get_auth_token(clazz, digest, email, password_digest):
    params = {
      'getauth': 1,
      'logout': 1,
      'digest': digest,
      'username': email,
      'passworddigest': password_digest,
    }
    url = clazz._make_api_url('userinfo')
    response  = requests.get(url, params = params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.json()
    assert 'auth' in payload
    return payload['auth']
  
  @classmethod
  def _make_api_url(clazz, method):
    return urlparse.urljoin(clazz.API, method)
