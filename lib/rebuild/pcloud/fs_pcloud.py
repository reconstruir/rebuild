#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.common.node import node
from bes.fs.file_attributes import file_attributes
from bes.fs.file_checksum import file_checksum
from bes.fs.file_checksum_db import file_checksum_db
from bes.fs.file_find import file_find
from bes.fs.file_metadata import file_metadata
from bes.fs.file_util import file_util
from bes.system.log import logger
from bes.factory.factory_field import factory_field

from bes.fs.fs.fs_base import fs_base
from bes.fs.fs.fs_file_info import fs_file_info
from bes.fs.fs.fs_file_info_list import fs_file_info_list
from bes.fs.fs.fs_error import fs_error

from rebuild.credentials.credentials import credentials

from .pcloud import pcloud

class fs_pcloud(fs_base):
  'pcloud filesystem'

  log = logger('fs')
  
  def __init__(self, credentials, root_dir = None, cache_dir = None):
    check.check_credentials(credentials)
    check.check_string(root_dir, allow_none = True)
    check.check_string(cache_dir, allow_none = True)
    self._cache_dir = cache_dir or path.expanduser('~/.bes/fs_pcloud/cache')
    self._pcloud = pcloud(credentials, root_dir or '/')
    self._credentials = credentials

  def __str__(self):
    return 'fs_pcloud(email={})'.format(self._credentials.email)


  @classmethod
  #@abstractmethod
  def creation_fields(clazz):
    'Return a list of fields needed for create()'
    return [
      factory_field('pcloud_email', False, check.is_string),
      factory_field('pcloud_password', False, check.is_string),
      factory_field('cache_dir', True, check.is_string),
      factory_field('root_dir', True, check.is_string),
    ]
  
  @classmethod
  #@abstractmethod
  def create(clazz, **values):
    'Create an fs instance.'
    pcloud_email = values['pcloud_email']
    pcloud_password = values['pcloud_password']
    cred = credentials.make_credentials(email = pcloud_email, password = pcloud_password)
    root_dir = values['root_dir']
    cache_dir = values['cache_dir']
    return fs_pcloud(cred, root_dir = root_dir, cache_dir = cache_dir)
    
  @classmethod
  #@abstractmethod
  def name(clazz):
    'The name if this fs.'
    return 'fs_pcloud'

  #@abstractmethod
  def list_dir(self, remote_dir, recursive):
    'List entries in a directory.'
    remote_dir = file_util.ensure_lsep(remote_dir)
    self.log.log_d('list_dir(remote_dir={}, recursive={}'.format(remote_dir, recursive))
    entries = self._pcloud.list_folder(folder_path = remote_dir, recursive = recursive, checksums = False)
    children = fs_file_info_list([ self._convert_pcloud_entry_to_fs_tree(entry, depth = 0) for entry in entries ])
    return fs_file_info(remote_dir, fs_file_info.DIR, None, None, None, children)

  def _convert_pcloud_entry_to_fs_tree(self, entry, depth = 0):
    indent = ' ' * depth
    is_file = not entry.is_folder
    remote_filename = entry.path
    if is_file:
      children = fs_file_info_list()
    else:
      children = fs_file_info_list([ self._convert_pcloud_entry_to_fs_tree(n, depth + 2) for n in entry.contents or [] ])
    return self._make_entry(remote_filename, entry, children)
    
  #@abstractmethod
  def has_file(self, remote_filename):
    'Return True if filename exists in the filesystem and is a FILE.'
    try:
      self.file_info(remote_filename)
      return True
    except fs_error as ex:
      return False
  
  #@abstractmethod
  def file_info(self, remote_filename):
    'Get info for a single file.'
    remote_filename = file_util.ensure_lsep(remote_filename)
    if remote_filename == '/':
      return fs_file_info(remote_filename, fs_file_info.DIR, None, None, None, fs_file_info_list())
    parent = path.dirname(remote_filename)
    basename = path.basename(remote_filename)
    entries = self._pcloud.list_folder(folder_path = parent)
    for entry in entries:
      if entry.name == basename:
        return self._make_entry(remote_filename, entry, fs_file_info_list())
    raise fs_error('file not found: {}'.format(remote_filename))

  def _make_entry(self, remote_filename, entry, children):
    if entry.is_folder:
      ftype = fs_file_info.DIR
    else:
      ftype = fs_file_info.FILE
    if ftype == fs_file_info.FILE:
      checksum = str(entry.content_hash)
      attributes = {}
      size = entry.size
    else:
      checksum = None
      attributes = None
      size = None
    return fs_file_info(file_util.lstrip_sep(remote_filename), ftype, size, checksum, attributes, children)

  #@abstractmethod
  def remove_file(self, filename):
    'Remove filename.'
    assert False
    
  #@abstractmethod
  def upload_file(self, filename, local_filename):
    'Upload filename from local_filename.'
    assert False

  #@abstractmethod
  def download_file(self, filename, local_filename):
    'Download filename to local_filename.'
    assert False
    
  #@abstractmethod
  def set_file_attributes(self, filename, attributes):
    'Set file attirbutes.'
    assert False
