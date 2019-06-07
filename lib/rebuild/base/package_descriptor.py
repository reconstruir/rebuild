#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from collections import namedtuple
from bes.common.check import check
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property
from bes.compat.cmp import cmp

from .build_version import build_version
from .requirement import requirement
from .requirement_list import requirement_list

class package_descriptor(namedtuple('package_descriptor', 'name, version, requirements, properties')):

  NAME_DELIMITER = '-'

  STR_PROPERTIES_DELIMITER = '; '

  PROPERTY_PKG_CONFIG_NAME = 'pkg_config_name'

  def __new__(clazz, name, version, requirements = None, properties = None):
    check.check_string(name)
    if not clazz.name_is_valid(name):
      raise RuntimeError('Invalid name: \"%s\"' % (name))
    version = build_version.validate_version(version)
    requirements = requirement_list(requirements)
    check.check_requirement_list(requirements)
    requirements = clazz.parse_requirements(requirements)
    properties = properties or {}
    check.check_dict(properties)
    return clazz.__bases__[0].__new__(clazz, name, version, requirements, properties)
  
  @cached_property
  def full_name(self):
    return self.make_full_name_str(self.name, self.version)

  @cached_property
  def tarball_filename(self):
    return '%s.tar.gz' % (self.full_name)

  def artifact_path(self, build_target):
    'Return the full path for an artifact made with this package info and the given build_target.'
    return path.join(build_target.build_path, self.tarball_filename)
  
  @classmethod
  def make_full_name_str(clazz, name, version):
    return '%s%s%s' % (name, clazz.NAME_DELIMITER, str(version))

  def __str__(self):
    part1 = self.full_name
    part2 = []
    if self.requirements:
      part2.append(self.requirements.to_string())
    if self.properties:
      part2.append(self.properties_to_string())
    part2 = self.STR_PROPERTIES_DELIMITER.join(part2)
    if part2:
      return '%s(%s)' % (part1, part2)
    else:
      return part1

  def __hash__(self):
    return hash(str(self))
    
  def properties_to_string(self):
    items = sorted(self.properties.items())
    return '; '.join([ '%s=%s' % (item[0], item[1]) for item in items ])

  def __eq__(self, other):
    check.check_package_descriptor(other)
    return hash(self) == hash(other)

  def __lt__(self, other):
    check.check_package_descriptor(other)
    name_rv = cmp(self.name, other.name)
    if name_rv < 0:
      return True
    version_rv = build_version.compare(self.version, other.version)
    if version_rv < 0:
      return True
    requirements_rv = cmp(self.requirements, other.requirements)
    if requirements_rv < 0:
      return True
    if self.properties.keys() < other.properties.keys():
      return True
    return False

  def to_json(self):
    return json.dumps(self.to_dict(), indent = 2, sort_keys = True)

  def to_dict(self):
    return {
      'name': self.name,
      'version': str(self.version),
      'requirements': [ req.to_string_colon_format() for req in self.requirements ],
      'properties': self.properties,
    }

  @classmethod
  def __dep_to_string(clazz, dep):
    assert isinstance(dep, requirement)
    assert dep.system_mask
    return '%s: %s' % (dep.system_mask, str(requirement(dep.name, dep.operator, dep.version, None)))
  
  @classmethod
  def parse_dict(clazz, d):
    assert 'name' in d
    assert 'version' in d
    requirements = clazz.parse_requirements(d.get('requirements', None))
    properties = d.get('properties', {})
    return package_descriptor(str(d['name']), str(d['version']),
                              requirements = requirements,
                              properties = properties,)

  @classmethod
  def parse_json(clazz, s):
    return clazz.parse_dict(json.loads(s))

  @classmethod
  def parse(clazz, s):
    sname = s.partition(clazz.NAME_DELIMITER)
    assert clazz.NAME_DELIMITER == sname[1]
    name = sname[0]
    version = sname[2]
    return package_descriptor(name, version)

  @classmethod
  def parse_requirements(clazz, requirements):
    requirements = requirements or []
    result = []
    for dep in requirements:
      if check.is_requirement(dep):
        result.append(dep)
      elif string_util.is_string(dep):
        reqs = requirement_list.parse(dep)
        result.extend(reqs)
      else:
        raise RuntimeError('Invalid requirement: %s - %s' % (str(dep), type(dep)))
    return requirement_list(result)

  @classmethod
  def name_is_valid(clazz, name):
    if not string_util.is_string(name):
      return False
    if not name:
      return False
    return True

  def extra_cflags(self, system):
    #config = self.properties.get('extra_cflags', [])
    #return reitred_masked_config.resolve_list(config, system)
    return []
    
  @property
  def pkg_config_name(self):
    'Return the name of the .pc file for pkg config this package uses.'
    return object_util.listify(self.properties.get(self.PROPERTY_PKG_CONFIG_NAME, [ self.name ]))

  @classmethod
  def full_name_cmp(clazz, pi1, pi2):
    'Compare name, version and revision and return an int either -1, 0, or 1'
    check.check_package_descriptor(pi1)
    check.check_package_descriptor(pi2)
    name_cmp = cmp(pi1.name, pi2.name)
    if name_cmp != 0:
      return name_cmp
    return build_version.compare(pi1.version, pi2.version)

  @cached_property
  def requirements_names(self):
    return set([ req.name for req in self.requirements ])

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
  def matches_requirement(self, req):
    check.check_requirement(req)
    if req.name != self.name:
      return False

    if req.version is None:
      return True

    if not req.operator:
      raise ValueError('missing operator: %s' % (str(req)))

    req_build_version = build_version.parse(req.version)
    assert req_build_version.epoch == 0
    v1 = self.version.upstream_version
    r1 = self.version.revision
    v2 = req_build_version.upstream_version
    r2 = req_build_version.revision
    
    cmp_result = build_version.compare_version_and_revision(v1, r1, v2, r2)
    #print('operator:%s: cmp(%s, %s, %s, %s) => %s' % (req.operator, v1, r1, v2, r2, cmp_result))
    
    if req.operator == '==':
      return cmp_result == 0
    elif req.operator == '>=':
      return cmp_result >= 0
    elif req.operator == '<=':
      return cmp_result <= 0
    elif req.operator == '>':
      return cmp_result > 0
    elif req.operator == '<':
      return cmp_result < 0
    else:
      raise ValueError('invalid operator \"%s\": %s' % (req.operator, str(req)))
  
check.register_class(package_descriptor, include_seq = False)
