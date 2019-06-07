#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common.check import check

from .hook_result import hook_result
from .hook_registry import hook_registry

class hook_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    hook_registry.register(clazz)
    return clazz

class hook(with_metaclass(hook_register_meta, object)):

  result = hook_result
  
  def __init__(self):
    'Create a new hook.'
    pass

  def __eq__(self, other):
    return self.__class__ == other.__class__

  def __str__(self):
    return self.__class__.__name__
  
  @abstractmethod
  def execute(self, script, env):
    'Execute the hook.  Same semantics as step.execute()'
    pass
    
check.register_class(hook)
