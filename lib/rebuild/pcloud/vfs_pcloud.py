#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from datetime import datetime

from bes.common.check import check
from bes.common.node import node
from bes.fs.file_attributes import file_attributes
from bes.fs.file_checksum import file_checksum
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.file_metadata import file_metadata
from bes.system.log import logger
from bes.factory.factory_field import factory_field
from bes.key_value.key_value_list import key_value_list
from bes.fs.checksum_set import checksum_set

from bes.vfs.vfs_base import vfs_base
from bes.vfs.vfs_path_util import vfs_path_util
from bes.vfs.vfs_file_info import vfs_file_info
from bes.vfs.vfs_file_info import vfs_file_info_list
from bes.vfs.vfs_error import vfs_error
from bes.vfs.vfs_path import vfs_path

from bes.credentials.credentials import credentials

from .pcloud import pcloud
from .pcloud_error import pcloud_error

class vfs_pcloud(vfs_base):
  'pcloud filesystem'

  log = logger('vfs_pcloud')
  
  def __init__(self, config_source, credentials, cache_dir = None):
    check.check_string(config_source)
    check.check_credentials(credentials)
    check.check_string(cache_dir, allow_none = True)

    self._config_source = config_source
    self._cache_dir = cache_dir or path.expanduser('~/.bes_vfs/vfs_pcloud')
    self._db_dir = path.join(self._cache_dir, 'db')
    self._db_metadata_filename = path.join(self._db_dir, 'metadata.db')
    self._db_checksum_filename = path.join(self._db_dir, 'checksum.db')
    self._pcloud = pcloud(credentials, '/')
    self._credentials = credentials

  def __str__(self):
    return 'vfs_pcloud(email={})'.format(self._credentials.email)

  @classmethod
  #@abstractmethod
  def creation_fields(clazz):
    'Return a list of fields needed for create()'
    return [
      factory_field('pcloud_email', False, check.is_string),
      factory_field('pcloud_password', False, check.is_string),
      factory_field('pcloud_cache_dir', True, check.is_string),
    ]
  
  @classmethod
  #@abstractmethod
  def create(clazz, config_source, **values):
    'Create an fs instance.'
    pcloud_email = values['pcloud_email']
    pcloud_password = values['pcloud_password']
    cred = credentials(config_source, email = pcloud_email, password = pcloud_password)
    cache_dir = values['pcloud_cache_dir']
    return vfs_pcloud(config_source, cred, cache_dir = cache_dir)
    
  @classmethod
  #@abstractmethod
  def name(clazz):
    'The name if this fs.'
    return 'vfs_pcloud'

  #@abstractmethod
  def list_dir(self, remote_dir, recursive, options):
    'List entries in a directory.'
    remote_dir = vfs_path_util.normalize(remote_dir)
    self.log.log_d('list_dir(remote_dir={}, recursive={}'.format(remote_dir, recursive))
    self._metadata_db_update_local()
    entries = self._pcloud.list_folder(folder_path = remote_dir, recursive = recursive, checksums = False)
    children = vfs_file_info_list([ self._convert_pcloud_entry_to_fs_tree(remote_dir, entry, depth = 0) for entry in entries ])
    return children

  def _convert_pcloud_entry_to_fs_tree(self, remote_dir, entry, depth = 0):
    indent = ' ' * depth
    is_file = not entry.is_folder
    remote_filename = entry.path
    if is_file:
      children = vfs_file_info_list()
    else:
      children = vfs_file_info_list([ self._convert_pcloud_entry_to_fs_tree(remote_dir, n, depth + 2) for n in entry.contents or [] ])
    return self._make_entry(remote_dir, remote_filename, entry, children)
    
  #@abstractmethod
  def has_file(self, remote_filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    try:
      self.file_info(remote_filename)
      return True
    except vfs_error as ex:
      return False
  
  #@abstractmethod
  def file_info(self, remote_filename, options):
    'Get info for a single file.'
    check.check_string(remote_filename)
    check.check_vfs_file_info_options(options, allow_none = True)

    remote_filename = vfs_path_util.normalize(remote_filename)

    self.log.log_d('file_info(remote_filename="{}", options={}'.format(remote_filename, options))
    
    if remote_filename == '/':
      return self._file_info_root(options)
    
    self._metadata_db_update_local()
    
    parent = vfs_path_util.dirname(remote_filename) or '/'
    basename = vfs_path_util.basename(remote_filename)

    self.log.log_d('file_info() parent="{}" basename="{}"'.format(parent, basename))
    
    entries = self._pcloud.list_folder(folder_path = parent)

    self.log.log_d('file_info() entries={}'.format(pprint.pformat(entries)))
    
    for entry in entries:
      if entry.name == basename:
        return self._make_entry(remote_filename,
                                entry,
                                vfs_file_info_list(),
                                options)
    raise vfs_error('file not found: {}'.format(remote_filename))

  def _file_info_root(self, options):
    entry = self._pcloud.folder_info(folder_path = '/')
    return self._make_entry('/', entry, vfs_file_info_list(), options)

  def _make_entry(self, remote_filename, entry, children, options):
    #print('X      remote_dir: {}'.format(remote_dir))
    #print('X remote_filename: {}'.format(remote_filename))
    #print('1 remote_filename: {}'.format(remote_filename))
    #remote_filename = vfs_path_util.normalize(remote_filename)
    #print('2 remote_filename: {}'.format(remote_filename))
    if entry.is_folder:
      ftype = vfs_file_info.DIR
    else:
      ftype = vfs_file_info.FILE
    if ftype == vfs_file_info.FILE:
      entry_path = remote_filename #vfs_path_util.normalize(vfs_path_util.join(remote_dir, vfs_path_util.lstrip_sep(remote_filename)))
      #print('entry_path: {}'.format(entry_path))
      chk = checksum_set(checksum(checksum.SHA256, self._metadata_db.get_value('checksums', entry_path, 'checksum.sha256')))
      attributes = self._metadata_db.get_values('attributes', entry_path).to_dict()
      size = entry.size
    else:
      chk = None
      attributes = None
      size = None
    modification_date = datetime.strptime(entry.modified, '%a, %d %b %Y %H:%M:%S +0000')
    #print('3 remote_filename: {}'.format(remote_filename))
    #print('          dirname: {}'.format(vfs_path_util.dirname(remote_filename)))
    #print('         basename: {}'.format(vfs_path_util.basename(remote_filename)))
    return vfs_file_info(remote_filename,
                         ftype,
                         modification_date,
                         size,
                         chk,
                         attributes,
                         children)

  #@abstractmethod
  def remove_file(self, remote_filename):
    'Remove filename.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    self._pcloud.delete_file(file_path = remote_filename)
    
  #@abstractmethod
  def upload_file(self, local_filename, remote_filename):
    'Upload filename from local_filename.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    sp = vfs_path_util.split_basename(remote_filename)
    self._metadata_db_update_local()
    checksum = file_util.checksum('sha256', local_filename)
    self._metadata_db.set_value('checksums', remote_filename, 'checksum.sha256', checksum)
    self._pcloud.upload_file(local_filename, sp.basename, folder_path = sp.dirname)
    self._metadata_db_update_remote()
    
  #@abstractmethod
  def download_to_file(self, remote_filename, local_filename):
    'Download filename to local_filename.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    self._pcloud.download_to_file(local_filename, file_path = remote_filename)
    
  #@abstractmethod
  def download_to_bytes(self, remote_filename):
    'Download filename to local_filename.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    return self._pcloud.download_to_bytes(file_path = remote_filename)
    
  #@abstractmethod
  def set_file_attributes(self, remote_filename, attributes):
    'Set file attirbutes.'
    remote_filename = vfs_path_util.normalize(remote_filename)
    self._metadata_db_update_local()
    self._metadata_db.replace_values('attributes', remote_filename,
                                     key_value_list.from_dict(attributes))
    self._metadata_db_update_remote()

  _METADATA_REMOTE_FILENAME = '/.bes_vfs/metadata.db'

  @property
  def _metadata_db(self):
    return file_metadata(path.dirname(self._db_metadata_filename),
                         db_filename = path.basename(self._db_metadata_filename))

  def _metadata_db_update_local(self):
    remote_checksum = self._metadata_remote_checksum()
    local_checksum = self._metadata_local_checksum()
    if remote_checksum == local_checksum:
      self.log.log_d('_metadata_db_update_local: local db up to date.')
      return
    self.log.log_d('_metadata_db_update_local: updating local db because checksum is different.')
    try:
      self._pcloud.download_to_file(self._db_metadata_filename, file_path = self._METADATA_REMOTE_FILENAME)
    except pcloud_error as ex:
      if ex.code in [ pcloud_error.PARENT_DIR_MISSING, pcloud_error.FILE_NOT_FOUND ]:
        self.log.log_d('_metadata_db_update_local: {} does not exist.'.format(self._METADATA_REMOTE_FILENAME))
        return
      raise

  def _metadata_db_update_remote(self):
    remote_checksum = self._metadata_remote_checksum()
    local_checksum = self._metadata_local_checksum()
    if remote_checksum == local_checksum:
      self.log.log_d('_metadata_db_update_remote: remote db up to date.')
    self.log.log_d('_metadata_db_update_remote: updating remote db because checksum is different.')
    sp = vfs_path_util.split_basename(self._METADATA_REMOTE_FILENAME)
    self._pcloud.upload_file(self._db_metadata_filename, sp.basename, folder_path = sp.dirname)

  def _metadata_remote_checksum(self):
    'Return the sha1 checksum for the remote metadata file.'
    try:
      return self._pcloud.checksum_file(file_path = self._METADATA_REMOTE_FILENAME)
    except pcloud_error as ex:
      if ex.code in [ pcloud_error.PARENT_DIR_MISSING, pcloud_error.FILE_NOT_FOUND ]:
        return None
      raise
    
  def _metadata_local_checksum(self):
    'Return the sha1 checksum for the local metadata file.'
    if not path.isfile(self._db_metadata_filename):
      return None
    return file_util.checksum('sha1', self._db_metadata_filename)
