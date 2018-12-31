#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from collections import namedtuple
from bes.common import check, node
from bes.key_value import key_value_list

from .recipe_error import recipe_error
from .recipe_util import recipe_util

class recipe(namedtuple('recipe', 'format_version, filename, enabled, properties, requirements, descriptor, instructions, steps, python_code, variables')):

  CHECK_UNKNOWN_PROPERTIES = True
  FORMAT_VERSION = 2
  
  def __new__(clazz, format_version, filename, enabled, properties, requirements,
              descriptor, instructions, steps, python_code, variables):
    check.check_int(format_version)
    check.check_recipe_enabled(enabled)
    if format_version != clazz.FORMAT_VERSION:
      raise recipe_error('Invalid recipe format_version %d' % (format_version))
    check.check_string(filename)
    check.check_string(python_code, allow_none = True)
    check.check_masked_value_list(variables, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, format_version, filename, enabled, properties,
                                      requirements, descriptor, instructions, steps, python_code, variables)

  def __str__(self):
    return self.to_string()

  def to_string(self, depth = 0, indent = 2):
    return recipe_util.root_node_to_string(self._to_node(), depth = depth, indent = indent)
  
  def _to_node(self):
    'A convenient way to make a recipe string is to build a graph first.'
    root = node('package %s %s %s' % (self.descriptor.name, self.descriptor.version.upstream_version, self.descriptor.version.revision))
    if self.python_code:
      root.children.append(recipe_util.python_code_to_node(self.python_code))
      root.add_child('')
    if self.enabled != '':
      root.add_child('enabled=%s' % (self.enabled.expression))
      root.add_child('')
    if self.variables:
      root.children.append(recipe_util.variables_to_node(self.variables))
      root.add_child('')
    if self.properties:
      root.children.append(self._properties_to_node(self.properties))
      root.add_child('')
    if self.requirements:
      root.children.append(self._requirements_to_node('requirements', self.requirements))
      root.add_child('')
    root.children.append(self._steps_to_node(self.steps))
    return root

  @classmethod
  def _requirements_to_node(clazz, label, requirements):
    result = node(label)
    for req in requirements:
      result.add_child(req.to_string_colon_format())
    return result
  
  @classmethod
  def _properties_to_node(clazz, properties):
    properties_node = node('properties')
    for key in sorted([ key for key in properties.keys()]):
      clazz._property_to_node(properties_node, key, properties)
    return properties_node
  
  @classmethod
  def _property_to_node(clazz, properties_node, key, properties):
    assert isinstance(properties_node, node)
    assert key in properties
    value = properties[key]
    if key in [ 'export_compilation_flags_requirements', 'extra_cflags' ]:
      properties_node.children.append(clazz._system_specific_property_to_node(key, properties))
    elif key in [ 'download_url', 'pkg_config_name' ]:
      properties_node.children.append(node('%s=%s' % (key, value)))
    else:
      if clazz.CHECK_UNKNOWN_PROPERTIES:
        raise RuntimeError('Unknown property: %s' % (key))
      else:
        properties_node.children.append(node('%s=%s' % (key, value)))
    del properties[key]

  @classmethod
  def _system_specific_property_to_node(clazz, key, properties):
    assert key in properties
    value = properties[key]
    check.check_masked_value_list(value)
    child = node(key)
    for i in value:
      child.add_child(i)
    return child

  @classmethod
  def _steps_to_node(clazz, steps):
    result = node('steps')
    for step in steps:
      step_node = result.add_child(step.name)
      for value in step.values:
        if len(value.values) == 1 and value.values[0].mask is None:
          step_node.add_child(str(value))
        else:
          value_node = step_node.add_child(value.key)
          for masked_value in value.values:
            masked_value_node = value_node.add_child(masked_value.to_string(quote = False))
      result.add_child('')
    return result

  @classmethod
  def _masked_value_list_to_node(clazz, key, mvl):
    result = node(key)
    for mv in mvl:
      result.add_child(mv.to_string())
    return result

  def resolve_variables(self, system):
    if not self.variables:
      return key_value_list()
    return self.variables.resolve(system, 'key_values')
  
check.register_class(recipe, include_seq = False)
