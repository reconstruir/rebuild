#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import sys
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common import check

from .hook_result import hook_result
from .hook_registry import hook_registry

class hook_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    hook_registry.register(clazz)
    hook_class_module_name = getattr(clazz, '__hook_class_module_name__', None)
#    if hook_class_module_name:
#      setattr(sys.modules[hook_class_module_name], clazz.__name__, clazz)
    return clazz

class hook(with_metaclass(hook_register_meta, object)):

  result = hook_result
  
  def __init__(self):
    'Create a new hook.'
    pass

  @abstractmethod
  def execute(self, script, env):
    'Execute the hook.  Same semantics as step.execute()'
    pass
    
check.register_class(hook)
