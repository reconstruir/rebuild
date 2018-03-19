#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

class requirement_manager(object):

  def __init__(self):
    self._packages = {}

  def add_package(self, descriptor):
    check.check_package_descriptor(descriptor)
    if descriptor.name in self._packages:
      raise ValueError('package \"%s\" already added.' % (descriptor.name))
    self._packages[descriptor.name] = descriptor

  def dependency_map(self, hardness, system):
    check.check_requirement_hardness_seq(descriptor)
    dep_map = {}
    for name, descriptor in self._packages.items():
      reqs = descriptor.caca_requirements.filter_by_hardness(hardness)
      
      
    
  '''
  @classmethod
  def _dependency_map(clazz, scripts, system):
    'Return a map of requirements dependencies.  A dictionary keyed on name pointing  to a set of dependencies.'
    assert isinstance(scripts, dict)
    dep_map = {}
    for name in sorted(scripts.keys()):
      script = scripts[name]
      requirements_names = script.descriptor.requirements_names_for_system(system)
      build_tool_requirements_names = script.descriptor.build_tool_requirements_names_for_system(system)
      build_requirements_names = script.descriptor.build_requirements_names_for_system(system)
      dep_map[name] = requirements_names | build_requirements_names | build_tool_requirements_names
    return dep_map
'''
  
check.register_class(requirement_manager, include_seq = False)
