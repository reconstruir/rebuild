#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import algorithm, check, dict_util, object_util
from bes.dependency import dependency_resolver, missing_dependency_error
from .requirement_list import requirement_list
from .requirement import requirement

class requirement_manager(object):

  def __init__(self):
    self._descriptor_map = {}
    self._is_tool_set = set()

  def __getitem__(self, key):
    return self._descriptor_map[key]
    
  def add_package(self, descriptor):
    check.check_package_descriptor(descriptor)
    name = descriptor.name
    if name in self._descriptor_map:
      raise ValueError('package \"%s\" already added.' % (name))
    self._descriptor_map[name] = descriptor
    tool_reqs = descriptor.requirements.filter_by_hardness(['TOOL'])
    self._is_tool_set |= set(tool_reqs.names())

  def is_tool(self, name):
    check.check_string(name)
    return name in self._is_tool_set

  def descriptors(self, names):
    check.check_string_seq(names)
    result = []
    for name in names:
      desc = self._descriptor_map.get(name, None)
      if not desc:
        raise ValueError('no such package found: %s' % (name))
      result.append(desc)
    return result
  
  @classmethod
  def print_dependency_map(clazz, dep_map, label):
    for name in sorted(dep_map.keys()):
      print('%s%s: %s' % (label, name, ' '.join(sorted(dep_map[name]))))
  
  def _resolve_deps(self, names, hardness, system):
    names = object_util.listify(names)
    hardness = self._normalize_hardness(hardness)
    reqs = requirement_list()
    for name in names:
      desc = self._descriptor_map.get(name, None)
      if not desc:
        raise KeyError('Not found in packages: %s' % (name))
      reqs.extend(desc.requirements.filter_by_hardness(hardness).filter_by_system(system))
    dep_map = self._dependency_map(hardness, system)
    return dependency_resolver.resolve_and_order_deps(reqs.names(), self._descriptor_map, dep_map)

  def _dependency_map(self, hardness, system):
    dep_map = {}
    for descriptor in self._descriptor_map.values():
      dep_map[descriptor.name] = set(descriptor.requirements.filter_by_hardness(hardness).filter_by_system(system).names())
    return dep_map

  @classmethod
  def _normalize_hardness(clazz, hardness):
    return sorted(object_util.listify(hardness))

  def resolve_tools(self, names, system):
    'Resolve what tools are needed for names and return the names in build order.'
    check.check_string_seq(names)
    just_deps = self._resolve_deps(names, [ 'BUILD', 'RUN', 'TOOL' ], system)
    just_deps_names = [ req.name for req in just_deps ]
    everything_names = algorithm.unique(just_deps_names + names)
    only_tool_names = [ dep for dep in everything_names if self.is_tool(dep) ]
    tool_just_deps = self._resolve_deps(only_tool_names, [ 'BUILD', 'RUN', 'TOOL' ], system)
    tool_just_deps_names = [ req.name for req in tool_just_deps ]
    tool_everything_names = algorithm.unique(tool_just_deps_names + only_tool_names)
    all_dep_map = self._dependency_map([ 'BUILD', 'RUN', 'TOOL' ], system)
    resolved_map = dict_util.filter_with_keys(all_dep_map, tool_everything_names)
    return self.descriptors(dependency_resolver.build_order_flat(resolved_map))

  def resolve(self, names, system):
    'Resolve packages without tools return the names in build order.'
    check.check_string_seq(names)
    just_deps = self._resolve_deps(names, [ 'BUILD', 'RUN' ], system)
    just_deps_names = [ req.name for req in just_deps ]
    everything_names = algorithm.unique(just_deps_names + names)
    only_non_tool_names = [ dep for dep in everything_names if not self.is_tool(dep) ]
    non_tool_just_deps = self._resolve_deps(only_non_tool_names, [ 'BUILD', 'RUN' ], system)
    non_tool_just_deps_names = [ req.name for req in non_tool_just_deps ]
    non_tool_everything_names = algorithm.unique(non_tool_just_deps_names + only_non_tool_names)
    all_dep_map = self._dependency_map([ 'BUILD', 'RUN' ], system)
    resolved_map = dict_util.filter_with_keys(all_dep_map, non_tool_everything_names)
    return self.descriptors(dependency_resolver.build_order_flat(resolved_map))

  def resolve_tools_deps(self, names, system):
    'Resolve what tools are needed for names and return the names in build order.'
    check.check_string_seq(names)
    just_deps = self._resolve_deps(names, [ 'BUILD', 'RUN', 'TOOL' ], system)
    just_deps_names = [ req.name for req in just_deps ]
    everything_names = algorithm.unique(just_deps_names)
    only_tool_names = [ dep for dep in everything_names if self.is_tool(dep) ]
    tool_just_deps = self._resolve_deps(only_tool_names, [ 'BUILD', 'RUN', 'TOOL' ], system)
    tool_just_deps_names = [ req.name for req in tool_just_deps ]
    tool_everything_names = algorithm.unique(tool_just_deps_names)
    all_dep_map = self._dependency_map([ 'BUILD', 'RUN', 'TOOL' ], system)
    resolved_map = dict_util.filter_with_keys(all_dep_map, tool_everything_names)
    return self.descriptors(dependency_resolver.build_order_flat(resolved_map))

  def resolve_deps(self, names, system):
    'Resolve packages without tools return the names in build order.'
    check.check_string_seq(names)
    just_deps = self._resolve_deps(names, [ 'BUILD', 'RUN' ], system)
    just_deps_names = [ req.name for req in just_deps ]
    everything_names = algorithm.unique(just_deps_names)
    only_non_tool_names = [ dep for dep in everything_names if not self.is_tool(dep) ]
    non_tool_just_deps = self._resolve_deps(only_non_tool_names, [ 'BUILD', 'RUN' ], system)
    non_tool_just_deps_names = [ req.name for req in non_tool_just_deps ]
    non_tool_everything_names = algorithm.unique(non_tool_just_deps_names)
    all_dep_map = self._dependency_map([ 'BUILD', 'RUN' ], system)
    resolved_map = dict_util.filter_with_keys(all_dep_map, non_tool_everything_names)
    return self.descriptors(dependency_resolver.build_order_flat(resolved_map))

  def resolve_deps_caca_tool(self, names, system, include_names):
    'Resolve packages without tools return the names in build order.'
    check.check_string_seq(names)
    just_deps = self._resolve_deps(names, [ 'TOOL' ], system)
    if include_names:
      all_deps = algorithm.unique(just_deps + self.descriptors(names))
    else:
      all_deps = just_deps
    return all_deps

  def resolve_deps_poto(self, names, system, hadrness, include_names):
    'Resolve dependencies.'
    check.check_string_seq(names)
    just_deps = self._resolve_deps(names, hadrness, system)
    if include_names:
      all_deps = algorithm.unique(just_deps + self.descriptors(names))
    else:
      all_deps = just_deps
    return all_deps

check.register_class(requirement_manager, include_seq = False)
