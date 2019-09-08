#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.common.node import node
from bes.fs.file_attributes import file_attributes
from bes.fs.file_checksum import file_checksum
from bes.fs.file_checksum_db import file_checksum_db
from bes.fs.file_find import file_find
from bes.fs.file_metadata import file_metadata
from bes.system.log import logger
from bes.factory.factory_field import factory_field

from bes.vfs.vfs_base import vfs_base
from bes.vfs.vfs_path import vfs_path
from bes.vfs.vfs_file_info import vfs_file_info
from bes.vfs.vfs_file_info import vfs_file_info_list
from bes.vfs.vfs_error import vfs_error

from rebuild.credentials.credentials import credentials

from .pcloud import pcloud

class vfs_pcloud(vfs_base):
  'pcloud filesystem'

  log = logger('fs')
  
  def __init__(self, config_source, credentials, cache_dir = None):
    check.check_string(config_source)
    check.check_credentials(credentials)
    check.check_string(cache_dir, allow_none = True)

    self._config_source = config_source
    self._cache_dir = cache_dir or path.expanduser('~/.bes/vfs_pcloud/cache')
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
  def list_dir(self, remote_dir, recursive):
    'List entries in a directory.'
    remote_dir = vfs_path.ensure_lsep(remote_dir)
    self.log.log_d('list_dir(remote_dir={}, recursive={}'.format(remote_dir, recursive))
    entries = self._pcloud.list_folder(folder_path = remote_dir, recursive = recursive, checksums = False)
    children = vfs_file_info_list([ self._convert_pcloud_entry_to_fs_tree(entry, depth = 0) for entry in entries ])
    return vfs_file_info(remote_dir, vfs_file_info.DIR, None, None, None, children)

  def _convert_pcloud_entry_to_fs_tree(self, entry, depth = 0):
    indent = ' ' * depth
    is_file = not entry.is_folder
    remote_filename = entry.path
    if is_file:
      children = vfs_file_info_list()
    else:
      children = vfs_file_info_list([ self._convert_pcloud_entry_to_fs_tree(n, depth + 2) for n in entry.contents or [] ])
    return self._make_entry(remote_filename, entry, children)
    
  #@abstractmethod
  def has_file(self, remote_filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    remote_filename = vfs_path.ensure_lsep(remote_filename)
    try:
      self.file_info(remote_filename)
      return True
    except vfs_error as ex:
      return False
  
  #@abstractmethod
  def file_info(self, remote_filename):
    'Get info for a single file.'
    remote_filename = vfs_path.ensure_lsep(remote_filename)
    if remote_filename == '/':
      return vfs_file_info(remote_filename, vfs_file_info.DIR, None, None, None, vfs_file_info_list())
    parent = path.dirname(remote_filename)
    basename = path.basename(remote_filename)
    entries = self._pcloud.list_folder(folder_path = parent)
    for entry in entries:
      if entry.name == basename:
        return self._make_entry(remote_filename, entry, vfs_file_info_list())
    raise vfs_error('file not found: {}'.format(remote_filename))

  def _make_entry(self, remote_filename, entry, children):
    if entry.is_folder:
      ftype = vfs_file_info.DIR
    else:
      ftype = vfs_file_info.FILE
    if ftype == vfs_file_info.FILE:
      checksum = str(entry.content_hash)
      attributes = {}
      size = entry.size
    else:
      checksum = None
      attributes = None
      size = None
    return vfs_file_info(vfs_path.lstrip_sep(remote_filename), ftype, size, checksum, attributes, children)

  #@abstractmethod
  def remove_file(self, remote_filename):
    'Remove filename.'
    remote_filename = vfs_path.ensure_lsep(remote_filename)
    self._pcloud.delete_file(file_path = remote_filename)
    
  #@abstractmethod
  def upload_file(self, local_filename, remote_filename):
    'Upload filename from local_filename.'
    remote_filename = vfs_path.ensure_lsep(remote_filename)
    sp = vfs_path.split_basename(remote_filename)
    self._pcloud.upload_file(local_filename, sp.basename, folder_path = sp.dirname)

  #@abstractmethod
  def download_to_file(self, remote_filename, local_filename):
    'Download filename to local_filename.'
    remote_filename = vfs_path.ensure_lsep(remote_filename)
    self._pcloud.download_to_file(local_filename, file_path = remote_filename)
    
  #@abstractmethod
  def download_to_bytes(self, remote_filename):
    'Download filename to local_filename.'
    remote_filename = vfs_path.ensure_lsep(remote_filename)
    return self._pcloud.download_to_bytes(file_path = remote_filename)
    
  #@abstractmethod
  def set_file_attributes(self, remote_filename, attributes):
    'Set file attirbutes.'
    remote_filename = vfs_path.ensure_lsep(remote_filename)
