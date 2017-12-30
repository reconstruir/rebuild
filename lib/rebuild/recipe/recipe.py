#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from collections import namedtuple
from bes.common import node

class recipe(namedtuple('recipe', 'format_version,filename,enabled,properties,requirements,build_requirements,descriptor,instructions,steps,load')):

  CHECK_UNKNOWN_PROPERTIES = True
  
  def __new__(clazz, format_version, filename, enabled, properties, requirements,
              build_requirements, descriptor, instructions, steps, load):
    return clazz.__bases__[0].__new__(clazz, format_version, filename, enabled, properties, requirements,
                                      build_requirements, descriptor, instructions, steps, load)

  def __str__(self):
    return self.to_string()

  def to_string(self, depth = 0, indent = 2):
    s = self._to_node().to_string(depth = depth, indent = indent).strip()
    lines = s.split('\n')
    for i, line in enumerate(lines):
      if line.isspace():
        lines[i] = ''
    return '\n'.join(lines)
  
  def _to_node(self):
    'A convenient way to make a recipe string is to build a graph first.'
    root = node('package %s' % (self.descriptor.full_name))
    if self.enabled != '':
      root.add_child('enabled=%s' % (self.enabled))
      root.add_child('')
    root.children.append(self._properties_to_node(self.properties))
    root.add_child('')
    if self.requirements:
      root.children.append(self._requirements_to_node('requirements', self.requirements))
      root.add_child('')
    if self.build_requirements:
      root.children.append(self._requirements_to_node('build_requirements', self.build_requirements))
      root.add_child('')
    root.children.append(self._steps_to_node(self.steps))
    if self.load:
      root.add_child('')
      root.children.append(self._load_to_node(self.load))
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
    if key == 'export_compilation_flags_requirements':
      properties_node.children.append(clazz._export_compilation_flags_requirements_to_node(properties))
    elif key in [ 'category' ]:
      properties_node.children.append(node('%s=%s' % (key, value)))
    else:
      if clazz.CHECK_UNKNOWN_PROPERTIES:
        raise RuntimeError('Unknown property: %s' % (key))
      else:
        properties_node.children.append(node('%s=%s' % (key, value)))
    del properties[key]

  @classmethod
  def _export_compilation_flags_requirements_to_node(clazz, properties):
    assert 'export_compilation_flags_requirements' in properties
    value = properties['export_compilation_flags_requirements']
    assert isinstance(value, list)
    child = node('export_compilation_flags_requirements')
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
  def _load_to_node(clazz, load):
    result = node('load')
    for l in load:
      result.add_child(l)
    return result
  
