#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import ABCMeta, abstractmethod
from bes.system.compat import with_metaclass
from bes.common import check, type_checked_list
from bes.dependency import dependency_provider
from .hook_registry import hook_registry
from .step_result import step_result

class hook_register_meta(ABCMeta):

  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    hook_registry.register_hook_class(clazz)
    return clazz

class hook(with_metaclass(hook_register_meta, dependency_provider)):

  step_result = step_result
  
  def __init__(self):
    'Create a new hook.'
    pass

  def value_to_string(self):
    return self.__class__.__name__
    
  @property
  def filename(self):
    filename = getattr(self, '__load_file__', None)
    if not filename:
      raise RuntimeError('filename not set')
    return filename

  def provided(self):
    'Return a list of dependencies provided by this provider.'
    return [ self.filename ]
    
  @abstractmethod
  def execute(self, script, env):
    'Execute the hook.  Same semantics as step.execute.'
    pass

class hook_list(type_checked_list, dependency_provider):

  def __init__(self, values = None):
    super(hook_list, self).__init__(hook, values = values)

  def __str__(self):
    return self.to_string()

  @classmethod
  def parse(clazz, value, hookname):
    result = clazz()
    filenames = string_list.parse(value, options = string_list.KEEP_QUOTES)
    for filename in filenames:
      rf = hook.parse(filename, hookname)
      result.append(hook.parse(filename, hookname))
    return result

  def provided(self):
    'Return a list of dependencies provided by this provider.'
    result = []
    for value in iter(self):
      result.extend(value.provided())
    return result

#check.register_class(hook, include_seq = False)
#check.register_class(hook_list, include_seq = False)
check.register_class(hook)
