#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.common.check import check
from bes.common.node import node
from bes.property.cached_property import cached_property
from bes.common.string_util import string_util
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.system.log import log
from bes.common.variable import variable

from rebuild.recipe.recipe_data_manager import recipe_data_manager
from rebuild.recipe.recipe_error import recipe_error
from rebuild.recipe.recipe_parser_util import recipe_parser_util
from rebuild.recipe.recipe_util import recipe_util
from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.recipe_data_manager import recipe_data_manager

from .ingest_method import ingest_method

class ingest_entry(namedtuple('ingest_entry', 'name, version, description, data, variables, method')):

  def __new__(clazz, name, version, description, data, variables, method):
    check.check_string(name)
    check.check_string(version)
    check.check_ingest_method(method)
    check.check_string(description, allow_none = True)
    check.check_masked_value_list(data, allow_none = True)
    check.check_masked_value_list(variables, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, name, version, description, data, variables, method)

  def __str__(self):
    return self.to_string().strip() + '\n'

  @cached_property
  def builtin_variables(self):
    return {
      'NAME': self.name,
      'VERSION': self.version,
    }

  def to_string(self, depth = 0, indent = 2):
    return recipe_util.root_node_to_string(self.to_node(), depth = depth, indent = indent)
  
  def to_node(self):
    root = node('entry {} {}'.format(self.name, self.version))
    root.add_child('')
    if self.description:
      root.children.append(recipe_util.description_to_node(self.description))
      root.add_child('')
    if self.data:
      root.children.append(recipe_util.variables_to_node('data', self.data))
      root.add_child('')
    if self.variables:
      root.children.append(recipe_util.variables_to_node('variables', self.variables))
      root.add_child('')
    if self.method:
      root.children.append(self.method.to_node())
      root.add_child('')
    return root

  def resolve_variables(self, system):
    if not self.variables:
      return key_value_list()
    return self.variables.resolve(system, 'key_values')
  
  def resolve_data(self, system):
    if not self.data:
      return []
    result = []
    for value in self.data:
      if value.mask_matches(system):
        result.append(tuple(value.value.value))
    return result

  def resolve_method_values(self, system, global_variables = None):
    check.check_dict(global_variables, allow_none = True)
    substitutions = self.resolve_variables(system).to_dict()
    substitutions.update(self.builtin_variables)
    substitutions.update(global_variables or {})
    result = self.method.resolve_values(system)
    result.substitute_variables(substitutions, patterns = variable.BRACKET)
    dm = recipe_data_manager()
    dm.set_from_tuples(self.resolve_data(system))
    for i, kv in enumerate(result):
      result[i] = key_value(kv.key, dm.substitute(kv.value))
    return result

  def data_substitutions(self, system):
    dm = recipe_data_manager()
    dm.set_from_tuples(self.resolve_data(system))
    return dm.substitutions()

  def download(self, system, global_variables, cache_dir, dest_dir):
    args = self.resolve_method_values(system, global_variables).to_dict()
    args['cache_dir'] = cache_dir
    return self.method.download(args)
  
check.register_class(ingest_entry, include_seq = False)