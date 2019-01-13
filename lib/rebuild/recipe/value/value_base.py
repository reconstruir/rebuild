#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from abc import abstractmethod, ABCMeta

from bes.system import log
from bes.system.compat import with_metaclass
from bes.common import check, variable
from bes.key_value import key_value_list

from .value_registry import value_registry
from .value_parsing import value_parsing
from .value_origin import value_origin
from .masked_value import masked_value

class value_register_meta(ABCMeta):

  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    value_registry.register(clazz)
    # add logging but only for the subclasses so log tags match the subclass
    if clazz.__name__ != 'value_base':
      log.add_logging(clazz, clazz.__name__)
    return clazz

class value_base(with_metaclass(value_register_meta, object)):
  
  def __init__(self, origin, properties = None):
    if origin:
      check.check_value_origin(origin)
    self.origin = origin
    properties = properties or key_value_list()
    check.check_key_value_list(properties)
    self._properties = properties
    self._substitutions = {}

  def __str__(self):
    return self.value_to_string(True)
  
  def __repr__(self):
    return repr(self.value)
  
  def properties_to_string(self):
    if not self._properties:
      return None
    return self._properties.to_string(value_delimiter = ' ', quote = True)

  @classmethod
  def parse_properties(clazz, text):
    return key_value_list.parse(text, options = key_value_list.KEEP_QUOTES)

  def get_property(self, key, default_value = None):
    kv = self._properties.find_by_key_backwards(key)
    if not kv:
      value = default_value
    else:
      value = kv.value
    if check.is_string(value):
      value = self.substitute(value)
    return value
  
  @property
  def substitutions(self):
    'Set substitutions.'
    return self._substitutions

  @property
  def properties(self):
    result = self._properties[:]
    result.substitute_variables(self._substitutions)
    return result

  @substitutions.setter
  def substitutions(self, substitutions):
    if self._substitutions == substitutions:
      return
    self._substitutions = substitutions
    self.substitutions_changed()
    
  def substitute(self, text):
    return variable.substitute(text, self._substitutions, patterns = variable.BRACKET)

  @abstractmethod
  def substitutions_changed(self):
    'substitutions changed.'
    assert False

  @abstractmethod
  def value_to_string(self, quote, include_properties = True):
    'Return the value as a string and quote if needed.'
    assert False
  
  @abstractmethod
  def sources(self, recipe_env, variables):
    'Return a list of sources this caca provides or None if no sources.'
    assert False

  @classmethod
  @abstractmethod
  def _parse_plain_string(clazz, origin, s):
    'Parse just a string.'
    assert False

  @classmethod
  def _call_parse_plain_string(clazz, origin, s):
    'Call _parse_plain_string with logging before and after for easy debugging.'
    clazz.log_d('_parse_plain_string: origin=%s; s=\"%s\"' % (origin, s))
    result = clazz._parse_plain_string(origin, s)
    clazz.log_d('_parse_plain_string: result=%s - %s' % (result, type(result)))
    return result
    
  @classmethod
  @abstractmethod
  def parse(clazz, origin, text, node):
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

  @classmethod
  def _new_parse_simple(clazz, value_type, origin, node):
    'Parse a value.'
    clazz.log_d('_new_parse_simple: value_type=%s; origin=%s; node=\n%s' % (value_type.__name__, origin, node.to_string(depth = 2)), multi_line = True)
    result = []
    root_text = node.data.text_no_comments
    clazz.log_d('_new_parse_simple: root_text=\"%s\"' % (root_text))
    if ':' in root_text:
      pv = value_parsing.parse_key_value(origin, root_text)
      clazz.log_d('_new_parse_simple: pv=%s' % (str(pv)))
      if pv.value:
        root_plain_value = clazz._call_parse_plain_string(origin, pv.value)
        root_masked_value = masked_value(None, value_type(origin = origin, value = root_plain_value))
        result.append(root_masked_value)
###    else:
###      root_text = root_text.strip()
###      if root_text:
###        root_plain_value = clazz._call_parse_plain_string(origin, root_text)
###        root_masked_value = masked_value(None, value_type(origin = origin, value = root_plain_value))
###        result.append(root_masked_value)
    for i, child in enumerate(node.children):
      child_origin = value_origin(origin.filename, child.data.line_number, child.data.text, origin.recipe_text)
      child_text = child.data.text_no_comments
      clazz.log_d('_new_parse_simple: %d: child_origin=%s; child_text=%s' % (i, child_origin, child_text))
      child_pv = value_parsing.parse_mask_and_value(child_origin, child_text)
      clazz.log_d('_new_parse_simple: %d: child_pv=%s' % (i, str(child_pv)))
      child_plain_value = clazz._call_parse_plain_string(child_origin, child_pv.value)
      clazz.log_d('_new_parse_simple: %d: child_plain_value=%s' % (i, child_plain_value))
      child_masked_value = masked_value(child_pv.mask, value_type(origin = child_origin, value = child_plain_value))
      clazz.log_d('_new_parse_simple: %d: child_masked_value=%s' % (i, str(child_masked_value)))
      result.append(child_masked_value)
    clazz.log_d('_new_parse_simple: result=%s' % (str(result)))
    return result
        
check.register_class(value_base)
