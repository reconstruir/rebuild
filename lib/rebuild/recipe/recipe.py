#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import node

class recipe(namedtuple('recipe', 'filename,enabled,properties,requirements,build_requirements,descriptor,instructions,steps')):

  def __new__(clazz, filename, enabled, properties, requirements, build_requirements,
              descriptor, instructions, steps):
    return clazz.__bases__[0].__new__(clazz, filename, enabled, properties, requirements,
                                      build_requirements, descriptor, instructions, steps)

  def __str__(self):
    return str(self._to_node()).strip()
  
  def _to_node(self):
    'A convenient way to make a recipe string is to build a graph first.'
    root = node('package %s' % (self.descriptor.full_name))
    root.add_child('')
    root.add_child('enabled=%s' % (self.enabled))
    root.add_child('')
    root.children.append(self._properties_to_node(self.properties))
    root.add_child('')
    root.children.append(self._requirements_to_node('requirements', self.requirements))
    root.add_child('')
    root.children.append(self._requirements_to_node('build_requirements', self.build_requirements))
    root.add_child('')
    root.children.append(self._steps_to_node(self.steps))
    return root

  @classmethod
  def _properties_to_node(clazz, properties):
    result = node('properties')
    for key, value in sorted(properties.items()):
      result.add_child('%s=%s' % (key, value))
    return result

  @classmethod
  def _requirements_to_node(clazz, label, requirements):
    result = node(label)
    for req in requirements:
      result.add_child(req.to_string_colon_format())
    return result

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
