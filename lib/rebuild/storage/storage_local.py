#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.system import log
from bes.fs import file_attributes, file_find, file_util
from bes.archive import archiver

from .storage_base import storage_base 
from .storage_address import storage_address

class storage_local(storage_base):

  def __init__(self, config):
    log.add_logging(self, 'storage_local')
    check.check_storage_factory_config(config)
    check.check_storage_config(config.storage_config)
    self._config = config
    sub_repo = self._config.sub_repo
    full_path = self._config.storage_config.full_path
    self.log_d('__init__: config=%s' % (str(config)))
    self.log_d('__init__: full_path=%s; sub_repo=%s' % (full_path, sub_repo))
    if sub_repo:
      self._where = path.join(self._config.storage_config.full_path, sub_repo)
    else:
      self._where = self._config.storage_config.full_path
    self._local_root_dir = config.local_cache_dir
    file_util.mkdir(self._where)
    file_util.mkdir(self._local_root_dir)
    self.log_d('__init__: _where=%s; _local_root_dir%s' % (self._where, self._local_root_dir))

  def make_address(self, filename = None):
    return storage_address(self._config.storage_config.location,
                           self._config.storage_config.repo,
                           self._config.storage_config.root_dir,
                           self._config.sub_repo,
                           filename)
    
  def __str__(self):
    return 'local:%s' % (self._where)

  #@abstractmethod
  def reload_available(self):
    # Nothing to do
    self.log_d('reload_available')
    pass
  
  #@abstractmethod
  def find_tarball(self, filename):
    local_filename = self._local_path(filename)
    if not path.isfile(local_filename):
      return None
    return local_filename

  #@abstractmethod
  def ensure_source(self, caca_filename):
    if caca_filename.startswith(self._local_root_dir):
      filename = file_util.remove_head(caca_filename, self._local_root_dir)
      filename_local = caca_filename
    else:
      filename = caca_filename
      filename_local = self._local_path(caca_filename)
      
    #assert local_filename.startswith(self._local_root_dir)
    #filename = file_util.remove_head(local_filename, self._local_root_dir)
    remote_path = self._remote_path(filename)
    self.log_d('ensure_source: filename_local=%s; remote_path=%s; filename=%s' % (filename_local, remote_path, filename))
    print('ensure_source: filename_local=%s; remote_path=%s; filename=%s' % (filename_local, remote_path, filename))
    if path.isfile(filename_local):
      return
    file_util.copy(remote_path, filename_local, use_hard_link = True)
  
  #@abstractmethod
  def search(self, name):
    name = name.lower()
    result = []
    for filename in self.list_all_files():
      if name in filename.lower():
        result.append(filename)
    return result

  #@abstractmethod
  def upload(self, local_filename, remote_filename, local_checksum):
    remote_path = self._remote_path(remote_filename)
    file_util.copy(local_filename, remote_path, use_hard_link = True)
    return True

  #@abstractmethod
  def set_properties(self, filename, properties):
    check.check_dict(properties)
    remote_path = self._remote_path(filename)
    for key, value in properties.items():
      check.check_string(key)
      if value is None:
        file_attributes.clear(remote_path, key)
      else:
        check.check_string(value)
        file_attributes.set(remote_path, key, value)
    return True
    
  #@abstractmethod
  def remote_checksum(self, remote_filename):
    remote_path = self._remote_path(remote_filename)
    if path.isfile(remote_path):
      return file_util.checksum('sha256', remote_path)
    return None
  
  #@abstractmethod
  def list_all_files(self):
    self.log_d('list_all_files: finding in %s' % (self._where))
    return archiver.find_archives(self._where, relative = True)

  def _local_path(self, filename):
    return path.join(self._local_root_dir, filename)

  def _remote_path(self, filename):
    return path.join(self._where, filename)
  
