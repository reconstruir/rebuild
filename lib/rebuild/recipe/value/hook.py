#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from abc import ABCMeta, abstractmethod
from bes.system.compat import with_metaclass
from bes.compat import StringIO
from bes.common import check, string_util, type_checked_list
from bes.dependency import dependency_provider

from .hook_registry import hook_registry
from .hook_result import hook_result
from .value_base import value_base
from .value_type import value_type
from .value_list_base import value_list_base

class hook_register_meta(ABCMeta):

  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    hook_registry.register_hook_class(clazz)
    return clazz

class hook(with_metaclass(hook_register_meta, value_base)):

  result = hook_result
  
  def __init__(self, env = None, properties = None):
    'Create a new hook.'
    super(hook, self).__init__(env, properties = properties)

  def __eq__(self, other):
    return self.filename == other.filename

  #@abstractmethod
  def value_to_string(self, quote):
    buf = StringIO()
    buf.write(self.__class__.__name__)
    ps = self.properties_to_string()
    if ps:
      buf.write(' ')
      buf.write(ps)
    return buf.getvalue()

  @classmethod
  #@abstractmethod
  def default_value(clazz, arg_type):
    'Return the default value to use for this class.'
    return hook_list()
  
  @property
  def filename(self):
    filename = getattr(self, '__load_file__', None)
    if not filename:
      raise RuntimeError('filename not set')
    return path.abspath(filename)

  #@abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    return [ self.filename ]

  #@abstractmethod
  def substitutions_changed(self):
    pass  

  @classmethod
  #@abstractmethod
  def parse(clazz, env, recipe_filename, value):
    hook_name, _, rest = string_util.partition_by_white_space(value)
    hook_class = hook_registry.get(hook_name)
    if not hook_class:
      raise TypeError('hook class not found: %s' % (hook_name))
    properties = clazz.parse_properties(rest)
    hook_instance = hook_class(env = env, properties = properties)
    return hook_instance

  @classmethod
  #@abstractmethod
  def resolve(clazz, values, arg_type):
    check.check_hook_seq(values)
    assert arg_type == value_type.HOOK_LIST
    env = None
    result_hooks = []
    for value in values:
      check.check_hook(value)
      if not env:
        env = value.env
      result_hooks.append(value)
    result = hook_list(env = env, values = result_hooks)
    result.remove_dups()
    return result
  
  @abstractmethod
  def execute(self, script, env):
    'Execute the hook.  Same semantics as step.execute.'
    pass

check.register_class(hook, include_seq = True)

#class hook_list(type_checked_list, dependency_provider):
#
#  __value_type__ = hook
#  
#  def __init__(self, values = None):
#    super(hook_list, self).__init__(values = values)
#
#  def __str__(self):
#    return ' '.join([ h.value_to_string() for h in iter(self) ])
#
#  @classmethod
#  def parse(clazz, value):
#    result = clazz()
#    names = string_list.parse(value, options = string_list.KEEP_QUOTES)
#    for name in names:
#      hook_class = hook_registry.get(name)
#      if not hook_class:
#        raise RuntimeError('hook class not found: %s' % (name))
#      hook = hook_class()
#      result.append(hook)
#    return result
#  
#  def provided(self):
#    'Return a list of dependencies provided by this provider.'
#    result = []
#    for value in iter(self):
#      result.extend(value.provided())
#    return result

class hook_list(value_list_base):

  __value_type__ = hook
  
  def __init__(self, env = None, values = None):
    super(hook_list, self).__init__(env = env, values = values)
  
check.register_class(hook_list, include_seq = False)
