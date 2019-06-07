#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re

from bes.common.check import check
from bes.common.string_util import string_util
from bes.text.string_list import string_list
from bes.system.log import logger

from rebuild.base import build_system

from .recipe_data_descriptor import recipe_data_descriptor
from .recipe_parser_util import recipe_parser_util
from .recipe_error import recipe_error

from .value import masked_value_list
from .value import value_factory
from .value import value_key_values
from .value import value_origin
from .value import masked_value
from .value import value_string_list

class recipe_data_manager(object):

  _LOG = logger('recipe_data_manager')
  
  def __init__(self):
    self._data = {}
   
  def set(self, ddesc, value):
    ddesc = self.resolve_data_descriptor(ddesc)
    if not ddesc.name in self._data:
      self._data[ddesc.name] = {}
    self._data[ddesc.name][ddesc.version] = value

  def set_from_tuple(self, desc_and_value):
    check.check_tuple(desc_and_value)
    if len(desc_and_value) != 3:
      raise ValueError('value should be 3 tuple of strings instead of: %s - %s' % (desc_and_value, type(desc_and_value)))
    check.check_string(desc_and_value[0])
    check.check_string(desc_and_value[1])
    check.check_string(desc_and_value[2])
    self.set(self.resolve_data_descriptor(desc_and_value), desc_and_value[2])

  def set_from_tuples(self, tuples):
    check.check_list(tuples, entry_type = tuple)
    for t in tuples:
      self.set_from_tuple(t)
    
  def has(self, ddesc):
    ddesc = self.resolve_data_descriptor(ddesc)
    return ddesc.name in self._data and ddesc.version in self._data[ddesc.name]

  def get(self, ddesc):
    ddesc = self.resolve_data_descriptor(ddesc)
    d = self._data.get(ddesc.name, None)
    if d is None:
      raise KeyError('No such data table: %s' % (ddesc.name))
    return d.get(ddesc.version, None)
  
  @classmethod
  def resolve_data_descriptor(clazz, o):
    if check.is_recipe_data_descriptor(o):
      return o
    elif check.is_string(o):
      return recipe_data_descriptor.parse(o)
    elif check.is_tuple(o):
      assert len(o) >= 2
      return recipe_data_descriptor(o[0], o[1])
    else:
      raise TypeError('Not a known recipe_data_descriptor type: %s - %s' % (o, type(o)))

  @classmethod
  def parse_node(clazz, node, filename):
    origin = value_origin(filename, node.data.line_number, node.data.text)
    if not node.data.text.startswith('data'):
      raise recipe_error.make_error('should start with \"data\"', filename, pkg_node = node)
    result = []
    for child in node.children:
      parts = string_list.parse(child.data.text)
      mask = clazz._yank_valid_mask(parts)
      value = masked_value(mask, value_string_list(origin = origin, value = parts), origin = origin)
      result.append(value)
      clazz._LOG.log_d('mask=%s; parts=%s; value=%s' % (mask, parts, value.value))
    return masked_value_list(result)
        
  @classmethod
  def _yank_valid_mask(clazz, parts):
    if len(parts) == 0:
      return None
    head = parts[0]
    if head.endswith(':'):
      possible_mask = head[0:-1]
      if build_system.mask_is_valid(possible_mask):
        parts.pop(0)
        return possible_mask
    return None

  def substitute(self, text):
    descs = recipe_data_descriptor.find(text)
    replacements = {}
    for desc in recipe_data_descriptor.find(text):
      value = self.get(desc)
      if not value:
        raise ValueError('No data found for: {}'.format(desc))
      replacements[str(desc)] = value
    return string_util.replace(text, replacements, word_boundary = False)
  
  def dump(self):
    import pprint
    print(pprint.pformat(self._data))
    
check.register_class(recipe_data_manager, include_seq = False)
