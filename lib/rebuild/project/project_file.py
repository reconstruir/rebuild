#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common.check import check
from bes.common.node import node
from bes.key_value.key_value_list import key_value_list
from bes.text.string_list import string_list

from rebuild.recipe import recipe_error
from rebuild.recipe.recipe_util import recipe_util

class project_file(namedtuple('project_file', 'format_version, filename, name, description, variables, imports, recipes, python_code')):

  FORMAT_VERSION = 2
  MAGIC = '!rebuild.project!'
  
  def __new__(clazz, format_version, filename, name, description, variables, imports, recipes, python_code):
    check.check_int(format_version)
    if format_version != clazz.FORMAT_VERSION:
      raise recipe_error('Invalid project_file format_version %d' % (format_version), filename, 1)
    check.check_string(filename)
    check.check_string(name)
    check.check_string(description, allow_none = True)
    check.check_key_value_list(variables, allow_none = True)
    check.check_masked_value_list(imports, allow_none = True)
    check.check_masked_value_list(recipes, allow_none = True)
    check.check_string(python_code, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, format_version, filename, name, description,
                                      variables, imports, recipes, python_code)

  def __str__(self):
    return self.to_string()

  def to_string(self, depth = 0, indent = 2):
    sproject = recipe_util.root_node_to_string(self._to_node(), depth = depth, indent = indent)
    return '{magic}\n{sproject}\n'.format(magic = self.MAGIC, sproject = sproject)
  
  def _to_node(self):
    'A convenient way to make a project_file string is to build a graph first.'
    root = node('project %s' % (self.name))
    if self.description:
      root.children.append(recipe_util.description_to_node(self.description))
      root.add_child('')
    if self.variables:
      root.children.append(self._variables_to_node(self.variables))
      root.add_child('')
    if self.imports:
      root.children.append(recipe_util.masked_value_list_to_node('imports', self.imports))
      root.add_child('')
    if self.recipes:
      root.children.append(recipe_util.masked_value_list_to_node('recipes', self.recipes))
      root.add_child('')
    if self.python_code:
      root.children.append(recipe_util.python_code_to_node(self.python_code))
      root.add_child('')
    return root

  def resolve_recipes(self, system):
    if not self.recipes:
      return string_list()
    return sorted(self.recipes.resolve(system, 'string_list'))
  
  def resolve_imports(self, system):
    if not self.imports:
      return string_list()
    return sorted(self.imports.resolve(system, 'string_list'))

  @classmethod
  def is_project_file(clazz, filename):
    'Return True if filename is a valid rebuild project file.'
    return recipe_util.file_starts_with_magic(filename, clazz.MAGIC)

  @classmethod
  def _variables_to_node(clazz, variables):
    check.check_key_value_list(variables)
    result = node('variables')
    for kv in variables:
      result.add_child(kv.to_string(quote_value = True))
    return result
  
check.register_class(project_file, include_seq = False)
