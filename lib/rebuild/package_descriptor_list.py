#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import dict_util, object_util, string_list
from .package_descriptor import package_descriptor
from rebuild.dependency import dependency_resolver

class package_descriptor_list(object):

  @classmethod
  def is_package_descriptor_list(clazz, descriptors):
    return object_util.is_homogeneous(descriptors, package_descriptor)

  @classmethod
  def dependency_map(clazz, descriptors):
    'Return a map of dependencies for the given descriptor list.'
    assert clazz.is_package_descriptor_list(descriptors)
    dep_map = {}
    for pd in descriptors:
      if dep_map.has_key(pd.name):
        raise RuntimeError('already in dependency map: %s' % (pd.name))
      dep_map[pd.name] = pd.requirements_names | pd.build_requirements_names
    return dep_map

  @classmethod
  def descriptor_map(clazz, descriptors):
    'Return a map for the given descriptor list.'
    assert clazz.is_package_descriptor_list(descriptors)
    desc_map = {}
    for pd in descriptors:
      if desc_map.has_key(pd.name):
        raise RuntimeError('already in descriptor map: %s' % (pd.name))
      desc_map[pd.name] = pd
    return desc_map

  # FIXME: doesnt belong here
  @classmethod
  def resolve_and_order_dependencies(clazz, names, descriptor_map, dependency_map):
    assert string_list.is_string_list(names)
    assert isinstance(descriptor_map, dict)
    assert isinstance(dependency_map, dict)
    resolved_names = dependency_resolver.resolve_deps(dependency_map, names)
    resolved = [ descriptor_map[name] for name in resolved_names ]
    resolved_map = dict_util.filter_with_keys(dependency_map, resolved_names)
    build_order = dependency_resolver.build_order_flat(resolved_map)
    resolved = [ descriptor_map[name] for name in build_order ]
    return resolved

  @classmethod
  def sort_by_name(clazz, descriptors):
    'Sort a list of descriptors in ascending order using package info.'
    assert clazz.is_package_list(descriptors)
    return sorted(descriptors, cmp = package_descriptor.full_name_cmp)

  @classmethod
  def latest_versions(clazz, descriptors):
    'Return a list of only the lastest version of any package with multiple versions.'
    assert clazz.is_package_list(descriptors)
    descriptors = clazz.sort_by_full_name(descriptors)
    d = {}
    for package in descriptors:
      d[package.info.name] = package
    return clazz.sort_by_descriptor(d.values())

  @classmethod
  def filter_out_by_name(clazz, descriptors, name):
    'Return a list of only the descriptors that dont match name.'
    assert clazz.is_package_descriptor_list(descriptors)
    return [ pd for pd in descriptors if pd.name != name ]
