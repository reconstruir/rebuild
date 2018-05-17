#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from abc import abstractmethod, ABCMeta

from bes.system.compat import with_metaclass
from bes.common import check, variable
from bes.key_value import key_value_list

from .value_registry import value_registry

class value_register_meta(ABCMeta):

  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    value_registry.register(clazz)
    return clazz

class value_base(with_metaclass(value_register_meta, object)):
  
  def __init__(self, env, origin, properties = None):
    if env:
      check.check_recipe_load_env(env)
    self.env = env
    if origin:
      check.check_value_origin(origin)
    self.origin = origin
    properties = properties or key_value_list()
    check.check_key_value_list(properties)
    self.properties = properties
    self._substitutions = {}

  def __str__(self):
    return self.value_to_string(True)

  @property
  def properties_dict(self):
    return self.properties.to_dict()
  
  def properties_to_string(self):
    if not self.properties:
      return None
    return self.properties.to_string(value_delimiter = ' ', quote = True)

  @classmethod
  def parse_properties(clazz, text):
    return key_value_list.parse(text, options = key_value_list.KEEP_QUOTES)

  decoded_properties = namedtuple('decoded_properties', 'dest, strip_common_base, base')
  
  def decode_properties(self):
    props = self.properties_dict
    dest = props.get('dest', '${REBUILD_SOURCE_UNPACKED_DIR}')
    dest = variable.substitute(dest, self._substitutions)
    base = props.get('base', None)
    if base:
      base = variable.substitute(base, self._substitutions)
    strip_common_base = props.get('strip_common_base', True)
    return self.decoded_properties(dest, strip_common_base, base)

  @property
  def substitutions(self):
    'Set substitutions.'
    return self._substitutions

  @substitutions.setter
  def substitutions(self, substitutions):
    if self._substitutions == substitutions:
      return
    self._substitutions = substitutions
    self.substitutions_changed()
    
  def substitute(self, text):
    return variable.substitute(text, self._substitutions)
    
  @abstractmethod
  def substitutions_changed(self):
    'substitutions changed.'
    assert False

  @abstractmethod
  def value_to_string(self, quote, include_properties = True):
    'Return the value as a string and quote if needed.'
    assert False
  
  @abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    assert False

  @classmethod
  @abstractmethod
  def parse(clazz, env, origin, text):
    'Parse a value.'
    assert False

  @classmethod
  @abstractmethod
  def default_value(clazz, class_name):
    'Return the default value to use for this class.'
    assert False

  @classmethod
  @abstractmethod
  def resolve(clazz, values, class_name):
    'Resolve a list of values if this type into a nice dictionary.'
    assert False

  def _append_properties_string(self, buf, include_properties):
    if include_properties:
      ps = self.properties_to_string()
      if ps:
        buf.write(' ')
        buf.write(ps)
    
check.register_class(value_base)
