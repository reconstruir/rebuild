#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common import check, variable
from bes.key_value import key_value_list

from collections import namedtuple

class value_base(with_metaclass(ABCMeta, object)):
  
  def __init__(self, env, properties = None):
    if env:
      check.check_recipe_load_env(env)
    self.env = env
    properties = properties or key_value_list()
    check.check_key_value_list(properties)
    self.properties = properties
    self._substitutions = {}

  def __str__(self):
    return self.value_to_string(True)
    
  def properties_to_string(self):
    if not self.properties:
      return None
    return self.properties.to_string(value_delimiter = ' ', quote = True)

  @classmethod
  def parse_properties(clazz, text):
    return key_value_list.parse(text, options = key_value_list.KEEP_QUOTES)

  decoded_properties = namedtuple('decoded_properties', 'dest, strip_common_base')
  
  def decode_properties(self):
    props = self.properties.to_dict()
    dest = props.get('dest', '${REBUILD_SOURCE_UNPACKED_DIR}')
    dest = variable.substitute(dest, self._substitutions)
    strip_common_base = props.get('strip_common_base', True)
    return self.decoded_properties(dest, strip_common_base)

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
    pass

  @abstractmethod
  def value_to_string(self, quote):
    'Return the value as a string and quote if needed.'
    pass
  
  @abstractmethod
  def sources(self):
    'Return a list of sources this caca provides or None if no sources.'
    pass

  @classmethod
  @abstractmethod
  def parse(clazz, env, recipe_filename, text):
    'Parse a value.'
    pass

  @classmethod
  @abstractmethod
  def default_value(clazz):
    'Return the default value to use for this class.'
    pass

  @classmethod
  @abstractmethod
  def resolve(clazz, values):
    'Resolve a list of values if this type into a nice dictionary.'
    pass

check.register_class(value_base)
