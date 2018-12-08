#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.common import check
from bes.system.compat import with_metaclass
from rebuild.base import build_target as BT

class recipe_load_env_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def get_build_target(self):
    raise NotImplementedError

  @abstractmethod
  def get_downloads_manager(self):
    raise NotImplementedError

  @abstractmethod
  def get_storage(self):
    raise NotImplementedError

  @property
  def build_target(self):
    return self.get_build_target()

  @property
  def downloads_manager(self):
    return self.get_downloads_manager()

  @property
  def storage(self):
    return self.get_storage()
  
class recipe_load_env(recipe_load_env_base):

  def __init__(self, builder_env):
    check.check_builder_env(builder_env)
    self._builder_env = builder_env

  #@abstractmethod
  def get_build_target(self):
    return self._builder_env.config.build_target

  #@abstractmethod
  def get_downloads_manager(self):
    return self._builder_env.downloads_manager

  #@abstractmethod
  def get_storage(self):
    return self._builder_env.storage

class testing_recipe_load_env(recipe_load_env_base):

  def __init__(self, build_target = None, downloads_manager = None, storage = None):
    build_target = build_target or BT.make_host_build_target()
    check.check_build_target(build_target)
    self._build_target = build_target
    if downloads_manager:
      check.check_git_download_cache(downloads_manager)
    self._downloads_manager = downloads_manager
    if storage:
      check.check_storage_chain(storage)
    self._storage = storage

  #@abstractmethod
  def get_build_target(self):
    return self._build_target

  #@abstractmethod
  def get_downloads_manager(self):
    return self._downloads_manager

  #@abstractmethod
  def get_storage(self):
    return self._storage
    
check.register_class(recipe_load_env_base, include_seq = False)
