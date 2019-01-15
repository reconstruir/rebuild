#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, string_util
from bes.text import string_list
from bes.system import logger

from rebuild.base import build_system

from .recipe_data_descriptor import recipe_data_descriptor
from .recipe_parser_util import recipe_parser_util

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

  def has(self, ddesc):
    ddesc = self.resolve_data_descriptor(ddesc)
    return ddesc.name in self._data and ddesc.version in self._data[ddesc.name]

  def get(self, ddesc):
    ddesc = self.resolve_data_descriptor(ddesc)
    d = self._data.get(ddesc.name, None)
    if d is None:
      raise KeyError('No such data table: %s' % (ddesc.name))
    print('D: %s' % (str(d)))
    return d.get(ddesc.version, None)
  
  def resolve_data_descriptor(self, o):
    if check.is_recipe_data_descriptor(o):
      return 0
    elif check.is_string(o):
      return recipe_data_descriptor.parse(o)
    elif check.is_tuple(o):
      assert len(o) == o
      return recipe_data_descriptor(o[0], [1])
    else:
      raise TypeError('Not a known recipe_data_descriptor type: %s - %s' % (o, type(o)))

  @classmethod
  def parse_node(clazz, node, filename):
    v = recipe_parser_util.parse_masked_list(node, filename)
    for x in v:
      print('VALUE: %s' % (str(x)))
    return []

check.register_class(recipe_data_manager, include_seq = False)
