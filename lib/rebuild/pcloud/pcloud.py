#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import hashlib, os.path as path
from io import BytesIO
from collections import namedtuple

from bes.system.log import log
from bes.common.check import check
from bes.common.node import node
from bes.property.cached_property import cached_property
from bes.fs.file_path import file_path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.text.string_list import string_list

from .pcloud_error import pcloud_error
from .pcloud_metadata import pcloud_metadata
from .pcloud_requests import pcloud_requests

from rebuild.credentials.credentials import credentials

class pcloud(object):

  API = 'https://api.pcloud.com'
  
  def __init__(self, credentials, root_dir):
    log.add_logging(self, 'pcloud')
    check.check_credentials(credentials)
    check.check_string(root_dir)
    self.credentials = credentials
    self.root_dir = root_dir

  @cached_property
  def digest(clazz):
    'Get a digest from pcloud to use with subsequent api calls.'
    response = pcloud_requests.get('getdigest', {})
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.payload
    assert 'digest' in payload
    return payload['digest']

  @cached_property
  def auth_token(self):
    password_digest = self._make_password_digest(self.digest, self.credentials.email, self.credentials.password)
    auth_token = self._get_auth_token(self.digest, self.credentials.email, password_digest)
    del self.credentials
    self.credentials = None
    return auth_token
  
  def list_folder(self, folder_path = None, folder_id = None, recursive = False, checksums = False):
    self.log_d('list_folder: folder_path=%s; folder_id=%s; recursive=%s; checksums=%s' % (folder_path, folder_id, recursive, checksums))
    if not folder_path and not folder_id:
      raise ValueError('Etiher folder_path or folder_id should be given.')
    elif folder_path and folder_id:
      raise ValueError('Only one of folder_path or folder_id should be given.')
    params = {
      'auth': self.auth_token,
      'recursive': int(recursive),
    }
    what = ''
    if folder_path:
      what = folder_path
      params.update({ 'path': folder_path })
    if folder_id:
      what = folder_id
      params.update({ 'folderid': folder_id })
    self.log_d('list_folder: params=%s' % (params))
    response = pcloud_requests.get('listfolder', params)
    self.log_d('list_folder: response=%s' % (str(response)))
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.payload
    assert 'result' in response.payload
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

  def quick_list_folder(self, folder_path, relative = True, recursive = False):
    items = self.list_folder(folder_path = folder_path, recursive = recursive)
    result = string_list()
    for item in items:
      result.extend(item.list_files())
    if not relative:
      result = string_list([ path.join(folder_path, f) for f in result ])
    result.sort()
    return result
  
  def delete_file(self, file_path = None, file_id = None):
    if not file_path and not file_id:
      raise ValueError('Etiher file_path or file_id should be given.')
    elif file_path and file_id:
      raise ValueError('Only one of file_path or file_id should be given.')
    params = {
      'auth': self.auth_token,
    }
    what = ''
    if file_path:
      what = file_path
      params.update({ 'path': file_path })
    if file_id:
      what = file_id
      params.update({ 'fileid': file_id })
    response = pcloud_requests.get('deletefile', params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.payload
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
    params = {
      'auth': self.auth_token,
    }
    what = ''
    if folder_path:
      params.update({ 'path': folder_path })
      what = folder_path
    else:
      params.update({ 'folderid': folder_id })
      params.update({ 'name': folder_name })
      what = '%s - %s' % (folderid, name)
    response = pcloud_requests.get('createfolder', params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.payload
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
      api_method = 'deletefolderrecursive'
    else:
      api_method = 'deletefolder'
    params = {
      'auth': self.auth_token,
    }
    what = ''
    if folder_path:
      params.update({ 'path': folder_path })
      what = folder_path
    else:
      params.update({ 'folderid': folder_id })
      what = folderid
    response = pcloud_requests.get(api_method, params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.payload
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
    params = {
      'auth': self.auth_token,
    }
    what = ''
    if file_path:
      what = file_path
      params.update({ 'path': file_path })
    if file_id:
      what = file_id
      params.update({ 'fileid': file_id })
    response = pcloud_requests.get('checksumfile', params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.payload
    assert 'result' in payload
    if payload['result'] != 0:
      raise pcloud_error(payload['result'], what)
    assert 'sha1' in payload
    return payload['sha1']

  def checksum_file_safe(self, file_path = None, file_id = None):
    'Checksum a file but return None if it does not exist.'
    assert file_path or file_id
    try:
      checksum = self.checksum_file(file_path = file_path, file_id = file_id)
    except pcloud_error as ex:
      self.log_d('caught exception trying to checksum: %s' % (str(ex)))
      if ex.code in [ pcloud_error.FILE_NOT_FOUND, pcloud_error.PARENT_DIR_MISSING ]:
        checksum = None
      else:
        raise ex
    return checksum
  
  getfilelink_result = namedtuple('getfilelink_result', 'path, expires, hosts')
  def getfilelink(self, file_path = None, file_id = None):
    if not file_path and not file_id:
      raise ValueError('Etiher file_path or file_id should be given.')
    elif file_path and file_id:
      raise ValueError('Only one of file_path or file_id should be given.')
    params = {
      'auth': self.auth_token,
    }
    what = ''
    if file_path:
      what = file_path
      params.update({ 'path': file_path })
    if file_id:
      what = file_id
      params.update({ 'fileid': file_id })
    response = pcloud_requests.get('getfilelink', params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.payload
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

    if cloud_filename != path.basename(local_path):
      old_local_path = local_path
      tmp_dir = temp_file.make_temp_dir()
      local_path = path.join(tmp_dir, cloud_filename)
      file_util.copy(old_local_path, local_path, use_hard_link = True)
    else:
      tmp_dir = None
    files = { cloud_filename: open(local_path, 'rb') }
    url = pcloud_requests.make_api_url('uploadfile')
    params = {
      'auth': self.auth_token,
      'filename': cloud_filename,
    }
    what = ''
    if folder_path:
      what = folder_path
      params.update({ 'path': folder_path })
    if folder_id:
      what = folder_id
      params.update({ 'folderid': folder_id })
    import requests
    try:
      response  = requests.post(url, data = params, files = files)
    finally:
      if tmp_dir:
        file_util.remove(tmp_dir)
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
    tmp = temp_file.make_temp_file(suffix = '.download')
    with open(tmp, 'wb') as fout:
      response = pcloud_requests.download_to_stream(links, fout)
      if response.status_code != 200:
        raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
      fout.close()
      file_util.copy(tmp, target)

  def download_to_bytes(self, file_path = None, file_id = None):
    'Download file to target.'
    links = self.getfilelink(file_path = file_path, file_id = file_id)
    buf = BytesIO()
    response = pcloud_requests.download_to_stream(links, buf)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    return buf.getvalue()
          
  @classmethod
  def _make_password_digest(clazz, digest, email, password):
    'Make a password digest.'
    email_digest = hashlib.sha1(email.lower().encode('utf-8')).hexdigest()
    password_digest_input = password + email_digest + digest
    digest_data = (password + email_digest + digest).encode('utf-8')
    return hashlib.sha1(digest_data).hexdigest()

  @classmethod
  def _get_auth_token(clazz, digest, email, password_digest):
    params = {
      'getauth': 1,
      'logout': 1,
      'digest': digest,
      'username': email,
      'passworddigest': password_digest,
    }
    response = pcloud_requests.get('userinfo', params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.payload
    if 'error' in payload:
      raise pcloud_error(payload['result'], '')
    assert 'auth' in payload
    return payload['auth']
  
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
    return clazz._make_item_node(pcloud_metadata(folder, '/', 0, True, 0, None, 'dir', '0', items or [], 0))

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
    params = {
      'auth': self.auth_token,
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
    response = pcloud_requests.get('file_open', params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.payload
    print('file_open: PAYLOAD: %s' % (payload))
    assert 'result' in payload
    if payload['result'] != 0:
      raise pcloud_error(payload['result'], what)
    assert 'fd' in payload
    return payload['fd']

  file_size_result = namedtuple('file_size_result', 'size, offset')
  def file_size(self, fd):
    params = {
      'auth': self.auth_token,
      'fd': fd,
    }
    what = str(fd)
    response = pcloud_requests.get('file_size', params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    payload = response.payload
    print('file_size: PAYLOAD: %s' % (payload))
    assert 'result' in payload
    if payload['result'] != 0:
      raise pcloud_error(payload['result'], what)
    assert 'size' in payload
    assert 'offset' in payload
    return self.file_size_result(payload['size'], payload['offset'])
  
  def file_write(self, fd, count):
    params = {
      'auth': self.auth_token,
      'fd': fd,
      'count': count,
    }
    what = str(fd)
    response = pcloud_requests.get('file_read', params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    import pprint
    print('RESPONSE: %s' % (pprint.pformat(response)))
    print('CONTENT: %s' % (response.content))
    print('CONTENT-TYPE: %s' % (response.content_type))
#    payload = response.payload
#    assert 'result' in payload
#    if payload['result'] != 0:
#      raise pcloud_error(payload['result'], what)
#    assert 'fd' in payload
#    return payload['fd']

  def file_read(self, fd, count):
    params = {
      'auth': self.auth_token,
      'fd': fd,
      'count': count,
    }
    what = str(fd)
    response = pcloud_requests.get('file_read', params)
    if response.status_code != 200:
      raise pcloud_error(error.HTTP_ERROR, str(response.status_code))
    import pprint
    print('RESPONSE: %s' % (pprint.pformat(response)))
    print('CONTENT: %s' % (response.content))
    print('CONTENT-TYPE: %s' % (response.content_type))
#    payload = response.payload
#    assert 'result' in payload
#    if payload['result'] != 0:
#      raise pcloud_error(payload['result'], what)
#    assert 'fd' in payload
#    return payload['fd']

  def make_path(self, f):
    return path.join(self.root_dir, f)
