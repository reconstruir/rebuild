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
  def get_git_downloads_manager(self):
    raise NotImplementedError

  @abstractmethod
  def get_sources_storage(self):
    raise NotImplementedError

  @property
  def build_target(self):
    return self.get_build_target()

  @property
  def git_downloads_manager(self):
    return self.get_git_downloads_manager()

  @property
  def storage(self):
    return self.get_sources_storage()
  
class recipe_load_env(recipe_load_env_base):

  def __init__(self, builder_env):
    check.check_builder_env(builder_env)
    self._builder_env = builder_env

  #@abstractmethod
  def get_build_target(self):
    return self._builder_env.config.build_target

  #@abstractmethod
  def get_git_downloads_manager(self):
    return self._builder_env.git_downloads_manager

  #@abstractmethod
  def get_sources_storage(self):
    return self._builder_env.sources_storage

class testing_recipe_load_env(recipe_load_env_base):

  def __init__(self, build_target = None):
    build_target = build_target or BT.make_host_build_target()
    check.check_build_target(build_target)
    self._build_target = build_target

  #@abstractmethod
  def get_build_target(self):
    return self._build_target

  #@abstractmethod
  def get_git_downloads_manager(self):
    assert False

  #@abstractmethod
  def get_sources_storage(self):
    assert False
    
check.register_class(recipe_load_env_base, include_seq = False)
