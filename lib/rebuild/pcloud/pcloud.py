#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib, os.path as path, requests
from io import BytesIO
from collections import namedtuple

from bes.compat.url_compat import urljoin
from bes.common import check, node
from bes.fs import file_path, file_util

from .pcloud_error import pcloud_error
from .pcloud_metadata import pcloud_metadata


class pcloud(object):

  API = 'https://api.pcloud.com'
  
  def __init__(self, credentials):
    check.check_pcloud_credentials(credentials)
    digest = self._get_digest()
    password_digest = self._make_password_digest(digest, credentials.email, credentials.password)
    self._auth_token = self._get_auth_token(digest, credentials.email, password_digest)
    self.root_dir = credentials.root_dir
    del credentials

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

  def folder_exists(self, folder_path):
    'Return True if the folder exists.'
    try:
      self.list_folder(folder_path = folder_path)
      return True
    except pcloud_error as ex:
      pass
    return False
  
  def ensure_folder(self, folder_path):
    'Ensure that the given folder exits.  Create all parents.'
    if not path.isabs(folder_path):
      raise ValueError('folder_path should be absolute: %s' % (folder_path))
    paths = file_path.decompose(folder_path)
    for p in paths:
      if not self.folder_exists(p):
        self.create_folder(folder_path = p)
  
  def delete_folder(self, folder_id = None, folder_path = None, recursive = False ):
    if not folder_path and not folder_id:
      raise ValueError('Etiher folder_path or folder_id should be given.')
    elif folder_path and folder_id:
      raise ValueError('Only one of folder_path or folder_id should be given.')
    if recursive:
      url = self._make_api_url('deletefolderrecursive')
    else:
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
    assert 'result' in payload
    if payload['result'] != 0:
      raise pcloud_error(payload['result'], what)
    return payload
  
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

  getfilelink_result = namedtuple('getfilelink_result', 'path, expires, hosts')
  def getfilelink(self, file_path = None, file_id = None):
    if not file_path and not file_id:
      raise ValueError('Etiher file_path or file_id should be given.')
    elif file_path and file_id:
      raise ValueError('Only one of file_path or file_id should be given.')
    url = self._make_api_url('getfilelink')
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
    assert 'path' in payload
    assert 'expires' in payload
    assert 'hosts' in payload#path, expires, hosts
    return self.getfilelink_result(payload['path'], payload['expires'], payload['hosts'])

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
      if folder_id:
        raise ex
      self.ensure_folder(folder_path)
    
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

  def download_to_file(self, target, file_path = None, file_id = None):
    'Download file to target.'
    links = self.getfilelink(file_path = file_path, file_id = file_id)
    url = 'https://{host}{path}'.format(host = links.hosts[0], path = links.path)
    req = requests.get(url, stream = True)
    file_util.ensure_file_dir(target)
    with open(target, 'wb') as fout:
      for chunk in req.iter_content(chunk_size = 1024): 
        if chunk: # filter out keep-alive new chunks
          fout.write(chunk)

  def download_to_bytes(self, file_path = None, file_id = None):
    'Download file to target.'
    links = self.getfilelink(file_path = file_path, file_id = file_id)
    url = 'https://{host}{path}'.format(host = links.hosts[0], path = links.path)
    req = requests.get(url, stream = True)
    buf = BytesIO()
    for chunk in req.iter_content(chunk_size = 1024): 
      if chunk: # filter out keep-alive new chunks
        buf.write(chunk)
    return buf.getvalue()
          
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
    return urljoin(clazz.API, method)

  @classmethod
  def _make_item_node(clazz, item):
    if item.is_folder:
      if item.name != '/':
        name = '%s/' % (item.name)
      else:
        name = '/'
    else:
      name = item.name
    n = node(item)
    for child in item.contents or []:
      child_node = clazz._make_item_node(child)
      n.children.append(child_node)
    return n

  @classmethod
  def items_to_tree(clazz, folder, items):
    return clazz._make_item_node(pcloud_metadata(folder, 0, True, 0, None, 'dir', '0', items or [], 0))

  # File flags from https://docs.pcloud.com/methods/fileops/file_open.html
  O_WRITE = 0x0002
  O_CREAT = 0x0040
  O_EXCL = 0x0080
  O_TRUNC = 0x0200
  O_APPEND = 0x0400

  # FIXME: check arguments for inconsistencies
  def file_open(self, flags, file_path = None, file_id = None, folder_id = None, filename = None):
    '''
    if not file_path and not file_id:
      raise ValueError('Etiher file_path or file_id should be given.')
    elif file_path and file_id:
      raise ValueError('Only one of file_path or file_id should be given.')
    '''
    url = self._make_api_url('file_open')
    params = {
      'auth': self._auth_token,
      'flags': flags,
    }
    what = [ file_path, file_id, folder_id ]
    what = ' - '.join([ x for x in what if x ])
    if file_path:
      params.update({ 'path': file_path })
    if file_id:
      params.update({ 'fileid': file_id })
    if folder_id:
      params.update({ 'folderid': folder_id })
    if filename:
      params.update({ 'name': filename })
    print('file_open params: %s' % (params))
    response = requests.get(url, params = params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.json()
    print('file_open: PAYLOAD: %s' % (payload))
    assert 'result' in payload
    if payload['result'] != 0:
      raise pcloud_error(payload['result'], what)
    assert 'fd' in payload
    return payload['fd']

  file_size_result = namedtuple('file_size_result', 'size, offset')
  def file_size(self, fd):
    url = self._make_api_url('file_size')
    params = {
      'auth': self._auth_token,
      'fd': fd,
    }
    what = str(fd)
    response = requests.get(url, params = params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.json()
    print('file_size: PAYLOAD: %s' % (payload))
    assert 'result' in payload
    if payload['result'] != 0:
      raise pcloud_error(payload['result'], what)
    assert 'size' in payload
    assert 'offset' in payload
    return self.file_size_result(payload['size'], payload['offset'])
  
  def file_read(self, fd, count):
    url = self._make_api_url('file_read')
    params = {
      'auth': self._auth_token,
      'fd': fd,
      'count': count,
    }
    what = str(fd)
    response = requests.get(url, params = params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    import pprint
    print('RESPONSE: %s' % (pprint.pformat(response)))
    print('CONTENT: %s' % (response.content))
    print('CONTENT-TYPE: %s' % (response.content_type))
#    payload = response.json()
#    assert 'result' in payload
#    if payload['result'] != 0:
#      raise pcloud_error(payload['result'], what)
#    assert 'fd' in payload
#    return payload['fd']

  def make_path(self, f):
    return path.join(self.root_dir, f)

