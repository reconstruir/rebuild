#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, dict_util, object_util, string_util
from .toposort import toposort, toposort_flatten

class cyclic_dependency_error(Exception):
  def __init__(self, message, cyclic_deps):
    super(cyclic_dependency_error, self).__init__(message)
    self.message = message
    self.cyclic_deps = cyclic_deps

  def __str__(self):
    return self.message
  
class missing_dependency_error(Exception):
  def __init__(self, message, missing_deps):
    super(missing_dependency_error, self).__init__()
    self.message = message
    self.missing_deps = missing_deps

  def __str__(self):
    return self.message
  
class dependency_resolver(object):

  ALL_DEPS = [ 'ALL_DEPS' ]

  @classmethod
  def build_order_flat(clazz, dep_map):
    'Return the build order for the given map of scripts.'
    return toposort_flatten(dep_map, sort = True)

  @classmethod
  def build_order(clazz, dep_map):
    'Return the build order for the given map of scripts.'
    return [ d for d in toposort(dep_map) ]

  @classmethod
  def check_missing(clazz, available, wanted):
    'Return a list of packages wanted but missing in available.'
    assert isinstance(available, ( list, set ))
    assert isinstance(wanted, ( list, set ))
    missing_set = set(wanted) - set(available)
    return sorted(list(missing_set))

  @classmethod
  def is_cyclic(clazz, dep_map):
    'Return True if the map has an cyclycal dependencies.'
    return len(clazz.cyclic_deps(dep_map)) > 0

  @classmethod
  def cyclic_deps(clazz, dep_map):
    'Return a list of dependencies in dep_map that that are cyclic.'
    try:
      clazz.build_order_flat(dep_map)
      return []
    except ValueError as ex:
      cyclic_deps = getattr(ex, 'cyclic_deps')
      return sorted(cyclic_deps.keys())

  @classmethod
  def resolve_deps(clazz, dep_map, names):
    '''
    Return a set of resolved dependencies for the given name or names.
    Sorted alphabetically, not in build order.
    '''

    cyclic_deps = clazz.cyclic_deps(dep_map)
    if len(cyclic_deps) > 0:
      raise cyclic_dependency_error('Cyclic dependencies found: %s' % (' '.join(cyclic_deps)), cyclic_deps)

    order = clazz.build_order_flat(dep_map)

    names = object_util.listify(names)
    result = set(names)
    for name in names:
      result |= clazz._resolve_deps(dep_map, name)
    return sorted(list(result))

  @classmethod
  def _resolve_deps(clazz, dep_map, name):
    'Return a set of resolved dependencies for the given name.  Not in build order.'
    assert string_util.is_string(name)
    if name not in dep_map:
      raise missing_dependency_error('Missing dependency: %s' % (name), [ name ])
    result = set()
    deps = dep_map[name]
    assert isinstance(deps, set)
    result |= deps
    for dep in deps:
      result |= clazz._resolve_deps(dep_map, dep)
    return result

  @classmethod
  def resolve_and_order_deps(clazz, names, descriptor_map, dependency_map):
    check.check_string_seq(names)
    check.check_dict(descriptor_map)
    check.check_dict(dependency_map)
    resolved_names = clazz.resolve_deps(dependency_map, names)
    resolved = [ descriptor_map[name] for name in resolved_names ]
    resolved_map = dict_util.filter_with_keys(dependency_map, resolved_names)
    build_order = clazz.build_order_flat(resolved_map)
    resolved = [ descriptor_map[name] for name in build_order ]
    return resolved
  
