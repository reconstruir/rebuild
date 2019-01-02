#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.system import log
from bes.fs import file_attributes, file_find, file_util
from bes.archive import archiver

from .storage_base import storage_base 
from .tarball_finder import tarball_finder

class storage_local(storage_base):

  def __init__(self, config):
    log.add_logging(self, 'storage_local')
    check.check_storage_factory_config(config)
    check.check_new_storage_config(config.storage_config)
    self._config = config
    location = path.expanduser(self._config.storage_config.location)
    repo = self._config.storage_config.repo
    root_dir = self._config.storage_config.root_dir
    sub_repo = self._config.sub_repo
    if root_dir:
      self._where = path.join(location, repo, root_dir, sub_repo)
    else:
      self._where = path.join(location, repo, sub_repo)
    self.log_e('__init__: location=%s; repo=%s; root_dir=%s; sub_repo=%s' % (location, repo, root_dir, sub_repo))
    self._local_root_dir = config.local_cache_dir
    file_util.mkdir(self._where)
    file_util.mkdir(self._local_root_dir)
    self.log_e('__init__: _where=%s; _local_root_dir%s' % (self._where, self._local_root_dir))
    
  def __str__(self):
    return 'local:%s' % (self._where)

  #@abstractmethod
  def reload_available(self):
    # Nothing to do
    self.log_d('reload_available')
    pass
  
  #@abstractmethod
  def find_tarball(self, filename):
    self.log_d('find_tarball: filename=%s' % (filename))
    available_files = archiver.find_archives(self._where, relative = True)
    for available_file in available_files:
      self.log_d('find_tarball: AVAILABLE: %s' % (available_file))
    if not filename in available_files:
      self.log_d('find_tarball: not found in available files: %s' % (filename))
      return None
    result = self._local_path(filename)
    self.log_d('find_tarball: %s found in available files => %s' % (filename, result))
    return result

  #@abstractmethod
  def ensure_source(self, local_filename):
    assert local_filename.startswith(self._local_root_dir)
    filename = file_util.remove_head(local_filename, self._local_root_dir)
    remote_path = self._remote_path(filename)
    self.log_d('ensure_source: local_filename=%s; remote_path=%s; filename=%s' % (local_filename, remote_path, filename))
    if path.isfile(local_filename):
      return
    file_util.copy(remote_path, local_filename, use_hard_link = True)
  
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
  def remote_filename_abs(self, remote_filename):
    assert False
    
  #@abstractmethod
  def remote_checksum(self, remote_filename):
    remote_path = self._remote_path(remote_filename)
    if path.isfile(remote_path):
      return file_util.checksum('sha256', remote_path)
    return None
  
  #@abstractmethod
  def list_all_files(self):
    return archiver.find_archives(self._where, relative = True)

  #@abstractmethod
  def _local_path(self, filename):
    return path.join(self._local_root_dir, filename)

  #@abstractmethod
  def _remote_path(self, filename):
    return path.join(self._where, filename)
  
