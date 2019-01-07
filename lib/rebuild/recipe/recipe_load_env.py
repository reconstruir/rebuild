#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta

from bes.common import check
from bes.system.compat import with_metaclass
from rebuild.base import build_target as BT

from .variable_manager import variable_manager

class recipe_load_env_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def _get_build_target(self):
    raise NotImplementedError

  @abstractmethod
  def _get_git_downloads_manager(self):
    raise NotImplementedError

  @abstractmethod
  def _get_sources_storage(self):
    raise NotImplementedError

  @abstractmethod
  def _get_variable_manager(self):
    raise NotImplementedError

  @property
  def build_target(self):
    return self._get_build_target()

  @property
  def git_downloads_manager(self):
    return self._get_git_downloads_manager()

  @property
  def storage(self):
    return self._get_sources_storage()
  
  @property
  def variable_manager(self):
    return self._get_variable_manager()
  
class recipe_load_env(recipe_load_env_base):

  def __init__(self, builder_env):
    check.check_builder_env(builder_env)
    self._builder_env = builder_env

  #@abstractmethod
  def _get_build_target(self):
    return self._builder_env.config.build_target

  #@abstractmethod
  def _get_git_downloads_manager(self):
    return self._builder_env.git_downloads_manager

  #@abstractmethod
  def _get_sources_storage(self):
    return self._builder_env.sources_storage

  #@abstractmethod
  def _get_variable_manager(self):
    return self._builder_env.variable_manager

class testing_recipe_load_env(recipe_load_env_base):

  def __init__(self, build_target = None):
    build_target = build_target or BT.make_host_build_target()
    check.check_build_target(build_target)
    self._build_target = build_target
    self._variable_manager = variable_manager()

  #@abstractmethod
  def _get_build_target(self):
    return self._build_target

  #@abstractmethod
  def _get_git_downloads_manager(self):
    assert False

  #@abstractmethod
  def _get_sources_storage(self):
    assert False
    
  #@abstractmethod
  def _get_variable_manager(self):
    return self._variable_manager
    
check.register_class(recipe_load_env_base, name = 'recipe_load_env', include_seq = False)
