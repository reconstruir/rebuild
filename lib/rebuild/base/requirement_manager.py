#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.common.object_util import object_util
from bes.dependency.dependency_resolver import dependency_resolver, missing_dependency_error
from bes.system.log import log
from bes.compat.StringIO import StringIO

from .package_descriptor_list import package_descriptor_list
from .requirement import requirement
from .requirement_list import requirement_list

class requirement_manager(object):

  def __init__(self):
    log.add_logging(self, 'requirement_manager')
    self._descriptor_map = {}
    self._is_tool_set = set()

  def __getitem__(self, key):
    return self._descriptor_map[key]
    
  def __eq__(self, other):
    check.check_requirement_manager(other)
    return self._descriptor_map == other._descriptor_map
    
  def add_package(self, pdesc):
    check.check_package_descriptor(pdesc)
    self.log_i('add_package(%s)' % (str(pdesc)))
    name = pdesc.name
    if name in self._descriptor_map:
      raise ValueError('package \"%s\" already added.' % (name))
    self._descriptor_map[name] = pdesc
    tool_reqs = pdesc.requirements.filter_by_hardness(['TOOL'])
    self._is_tool_set |= set(tool_reqs.names())
    
  def add_packages(self, packages):
    check.check_package_descriptor_list(packages)
    for pdesc in packages:
      self.add_package(pdesc)
    
  def is_tool(self, name):
    check.check_string(name)
    return name in self._is_tool_set

  def descriptors(self, names):
    check.check_string_seq(names)
    result = package_descriptor_list()
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
  
  def descriptor_map_to_string(self):
    buf = StringIO()
    for k, v in self._descriptor_map.items():
      buf.write('%s: %s\n' % (k, str(v)))
    return buf.getvalue().strip()

  def dependency_map(self, hardness, system):
    dep_map = {}
    for descriptor in self._descriptor_map.values():
      dep_map[descriptor.name] = set(descriptor.requirements.filter_by(hardness, system).names())
    return dep_map

  @classmethod
  def _normalize_hardness(clazz, hardness):
    return sorted(object_util.listify(hardness))
  
  def resolve_deps(self, names, system, hardness, include_names):
    'Resolve dependencies.'
    self.log_i('resolve_deps(names=%s, system=%s, hardness=%s, include_names=%s)' % (' '.join(names),
                                                                                     system, ' '.join(hardness),
                                                                                     include_names))
    check.check_string_seq(names)
    names = object_util.listify(names)
    hardness = self._normalize_hardness(hardness)
    reqs = requirement_list()
    for name in names:
      desc = self._descriptor_map.get(name, None)
      if not desc:
        raise KeyError('Not found in packages: %s' % (name))
      reqs.extend(desc.requirements.filter_by(hardness, system))
    self.log_i('resolve_deps() reqs=%s' % (str(reqs.names())))
    dep_map = self.dependency_map(hardness, system)
    result = package_descriptor_list(dependency_resolver.resolve_and_order_deps(reqs.names(), self._descriptor_map, dep_map))
    self.log_i('resolve_deps() 1 result=%s' % (str(result.names())))
    if include_names:
      result += self.descriptors(names)
    result.remove_dups()
    self.log_i('resolve_deps() 2 result=%s' % (str(result.names())))
    return result

  _resolve_result = namedtuple('_resolve_result', 'resolved, missing')
  def resolve_deps_NEW(self, names, system, hardness, include_names):
    'Resolve dependencies.'
    self.log_i('resolve_deps(names=%s, system=%s, hardness=%s, include_names=%s)' % (' '.join(names),
                                                                                     system, ' '.join(hardness),
                                                                                     include_names))
    check.check_string_seq(names)
    names = object_util.listify(names)
    hardness = self._normalize_hardness(hardness)
    reqs = requirement_list()
    missing = []
    for name in names:
      desc = self._descriptor_map.get(name, None)
      if desc:
        reqs.extend(desc.requirements.filter_by(hardness, system))
      else:
        missing.append(name)
    if missing:
      return self._resolve_result(None, missing)
    self.log_i('resolve_deps() reqs=%s' % (str(reqs.names())))
    dep_map = self.dependency_map(hardness, system)
    result = package_descriptor_list(dependency_resolver.resolve_and_order_deps(reqs.names(), self._descriptor_map, dep_map))
    self.log_i('resolve_deps() 1 result=%s' % (str(result.names())))
    if include_names:
      result += self.descriptors(names)
    result.remove_dups()
    self.log_i('resolve_deps() 2 result=%s' % (str(result.names())))
    return self._resolve_result(result, None)

check.register_class(requirement_manager, include_seq = False)
