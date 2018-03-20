#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from bes.dependency import dependency_resolver, missing_dependency_error

class requirement_manager(object):

  def __init__(self):
    self.descriptor_map = {}
    self.dependency_map = {}

  def add_package(self, descriptor):
    check.check_package_descriptor(descriptor)
    if descriptor.name in self.descriptor_map:
      raise ValueError('package \"%s\" already added.' % (descriptor.name))
    self.descriptor_map[descriptor.name] = descriptor
    self.dependency_map[descriptor.name] = set(descriptor.caca_requirements.names())

  @classmethod
  def print_dependency_map(clazz, dep_map, label):
    for name in sorted(dep_map.keys()):
      print('%s%s: %s' % (label, name, ' '.join(sorted(dep_map[name]))))
  
  def resolve(self, name, hardness, system):
    desc = self.descriptor_map.get(name, None)
    if not desc:
      raise KeyError('Not found in packages: %s' % (name))
    reqs = desc.caca_requirements.filter_by_hardness(hardness).filter_by_system(system)
    return dependency_resolver.resolve_and_order_deps(reqs.names(), self.descriptor_map, self.dependency_map)
    
  @classmethod
  def _resolve_and_order_dependencies(clazz, names, scripts, dependency_map):
    return dependency_resolver.resolve_and_order_deps(names, descriptor_map, dependency_map)
    
check.register_class(requirement_manager, include_seq = False)
