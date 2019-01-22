#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from collections import namedtuple
from bes.common import check, node, variable
from bes.key_value import key_value_list
from bes.text import string_list

from rebuild.recipe import recipe_error
from rebuild.recipe.recipe_util import recipe_util
from rebuild.base import requirement_list

class venv_project_config(namedtuple('venv_project_config', 'format_version, filename, name, description, variables, packages, python_code')):

  FORMAT_VERSION = 2
  MAGIC = '!rebuild.revenv!'
  
  def __new__(clazz, format_version, filename, name, description, variables, packages, python_code):
    check.check_int(format_version)
    if format_version != clazz.FORMAT_VERSION:
      raise recipe_error('Invalid venv_config format_version %d' % (format_version), filename, 1)
    check.check_string(name)
    check.check_string(description, allow_none = True)
    check.check_masked_value_list(variables, allow_none = True)
    check.check_requirement_list(packages, allow_none = True)
    check.check_string(python_code, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, format_version, filename, name, description,
                                      variables, packages, python_code)

  def __str__(self):
    return self.to_string()

  def to_string(self, depth = 0, indent = 2):
    sproject = recipe_util.root_node_to_string(self._to_node(), depth = depth, indent = indent)
    return '{magic}\n{sproject}\n'.format(magic = self.MAGIC, sproject = sproject)
  
  def _to_node(self):
    'A convenient way to make a venv_config string is to build a graph first.'
    root = node(self.name)
    if self.description:
      root.children.append(recipe_util.description_to_node(self.description))
      root.add_child('')
    if self.variables:
      root.children.append(recipe_util.variables_to_node(self.variables))
      root.add_child('')
    if self.packages:
      root.children.append(recipe_util.requirements_to_node('packages', self.packages))
      root.add_child('')
    if self.python_code:
      root.children.append(recipe_util.python_code_to_node(self.python_code))
      root.add_child('')
    return root

  def resolve_variables(self, system):
    if not self.variables:
      return key_value_list()
    return self.variables.resolve(system, 'key_values')
  
  def resolve_packages(self, system):
    if not self.packages:
      return requirement_list()
    project_substitutions = self.resolve_variables(system).to_dict()
    env_substitutions = dict(os.environ)
    result = requirement_list()
    for req in self.packages.resolve(system):
      # Give the shell environment the first crack
      if not req.version:
        resolved_req = req
      else:
        version = variable.substitute(req.version, env_substitutions, word_boundary = False)
        version = variable.substitute(version, project_substitutions, word_boundary = False)
        resolved_req = req.clone(mutations = { 'version': version })
      result.append(resolved_req)
    return result
  
  @classmethod
  def is_venv_config(clazz, filename):
    'Return True if filename is a valid venv_config file.'
    return recipe_util.file_starts_with_magic(filename, clazz.MAGIC)
  
check.register_class(venv_project_config, include_seq = False)
