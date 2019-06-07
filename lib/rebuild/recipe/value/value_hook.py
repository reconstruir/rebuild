#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from abc import ABCMeta, abstractmethod
from bes.system.compat import with_metaclass
from bes.compat.StringIO import StringIO
from bes.common.check import check
from bes.common.string_util import string_util
from bes.common.type_checked_list import type_checked_list

from bes.dependency import dependency_provider

from .hook_result import hook_result

from .masked_value import masked_value
from .value_base import value_base
from .value_list_base import value_list_base
from .value_origin import value_origin
from .value_parsing import value_parsing
from .value_type import value_type
from .hook import hook

class value_hook(value_base):

  result = hook_result
  
  def __init__(self, origin = None, value = None, properties = None):
    'Create a new hook inline.'
    assert not properties
    super(value_hook, self).__init__(origin, properties = properties)
    if value:
      check.check_hook(value)
    self.value = value

  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self, other):
    return self.value == other.value

  #@abstractmethod
  def value_to_string(self, quote, include_properties = True):
    return str(self.value)

  @classmethod
  #@abstractmethod
  def default_value(clazz, class_name):
    'Return the default value to use for this class.'
    return value_hook_list()
  
#  @property
#  def filename(self):
#    filename = getattr(self, '__load_file__', None)
#    if not filename:
#      raise RuntimeError('filename not set')
#    return path.abspath(filename)

  #@abstractmethod
  def sources(self, recipe_env, variables):
    'Return a list of sources this caca provides or None if no sources.'
    return []

  #@abstractmethod
  def substitutions_changed(self):
    pass  

  @classmethod
  #@abstractmethod
  def parse(clazz, origin, value, node):
    assert False

  @classmethod
  #@abstractmethod
  def new_parse(clazz, origin, node):
    'Parse a value.'
    result = []
    for child in node.children:
      child_origin = value_origin(origin.filename, child.data.line_number, child.data.text)
      child_pv = value_parsing.parse_mask_and_value(child_origin, child.get_text(child.NODE))
      hook_class_name = child_pv.value
      if not hook_class_name:
        value_parsing.raise_error(child_origin, 'Hook class name missing')
      hook_code = child.get_text(child.CHILDREN_INLINE)
      c = compile(hook_code, child_origin.filename, 'exec')
      exec_locals = {}
      exec(c, globals(), exec_locals)
      if hook_class_name not in exec_locals:
        value_parsing.raise_error(child_origin, 'Hook class not found: %s' % (hook_class_name))
      hook_class = exec_locals[hook_class_name]
      hook = hook_class()
      child_masked_value = masked_value(child_pv.mask, value_hook(origin = origin, value = hook))
      result.append(child_masked_value)
    return result
  
  @classmethod
  #@abstractmethod
  def resolve(clazz, values, class_name):
    check.check_value_hook_seq(values)
    assert class_name == value_type.HOOK
    result_hooks = []
    for value in values:
      check.check_value_hook(value)
      result_hooks.append(value)
    result = value_hook_list(value = result_hooks)
    result.remove_dups()
    return result
  
  def execute(self, script, env):
    'Execute the hook.  Same semantics as step.execute.'
    return self.value.execute(script, env)

  @classmethod
  #@abstractmethod
  def _parse_plain_string(clazz, origin, s):
    'Parse just a string.'
    assert False
  
check.register_class(value_hook, include_seq = True)

class value_hook_list(value_list_base):

  __value_type__ = value_hook
  
  def __init__(self, origin = None, value = None):
    super(value_hook_list, self).__init__(origin = origin, value = value)

  @classmethod
  #@abstractmethod
  def _parse_plain_string(clazz, origin, s):
    'Parse just a string.'
    assert False
    
check.register_class(value_hook_list, include_seq = False)
