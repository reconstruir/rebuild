#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from bes.common import object_util, string_util
from bes.compat import cmp
from rebuild.dependency import dependency_resolver
from .Category import Category
from .System import System
from .build_target import build_target
from collections import namedtuple
from .requirement import requirement
from .version import version
from .platform_specific_config import platform_specific_config as psc

class package_descriptor(object):

  NAME_DELIMITER = '-'

  STR_PROPERTIES_DELIMITER = '; '

  PROPERTY_CATEGORY = 'category'
  PROPERTY_DISABLED = 'disabled'
  PROPERTY_ENV_VARS = 'env_vars'
  PROPERTY_PKG_CONFIG_NAME = 'pkg_config_name'
  
  def __init__(self, name, ver, requirements = None, build_requirements = None, properties = None):
    requirements = requirements or []
    build_requirements = build_requirements or []
    properties = properties or {}

    if not self.name_is_valid(name):
      raise RuntimeError('Invalid name: \"%s\"' % (name))
    self._name = name
    self._version = version.validate_version(ver)

    self._requirements = self.parse_requirements(requirements)
    self._resolved_requirements = None

    self._build_requirements = self.parse_requirements(build_requirements)
    self._resolved_build_requirements = None

    self._properties = properties

  @property
  def name(self):
    return self._name

  @name.setter
  def name(self, value):
    raise RuntimeError('name is immutable.')

  @property
  def version(self):
    return self._version

  @version.setter
  def version(self, value):
    raise RuntimeError('version is immutable.')

  @property
  def requirements(self):
    return self._requirements

  @requirements.setter
  def requirements(self, value):
    raise RuntimeError('requirements are immutable.')

  @property
  def build_requirements(self):
    return self._build_requirements

  @build_requirements.setter
  def build_requirements(self, value):
    raise RuntimeError('build_requirements are immutable.')

  @property 
  def properties(self):
    return self._properties
  
  @properties.setter
  def properties(self, value):
    raise RuntimeError('properties are immutable.')

  @property
  def resolved_requirements(self):
    return self._resolved_requirements or []

  @resolved_requirements.setter
  def resolved_requirements(self, value):
    if self._resolved_requirements != None:
      raise RuntimeError('resolved_requirements can only be set once')
    if not self.is_package_info_list(value):
      raise RuntimeError('resolved_requirements should be a list of package_descriptor objects: %s' % (str(value)))
    self._resolved_requirements = value

  @property
  def resolved_build_requirements(self):
    return self._resolved_build_requirements or []

  @resolved_build_requirements.setter
  def resolved_build_requirements(self, value):
    if self._resolved_build_requirements != None:
      raise RuntimeError('resolved_build_requirements can only be set once')
    if not self.is_package_info_list(value):
      raise RuntimeError('resolved_build_requirements should be a list of package_descriptor objects: %s' % (str(value)))
    self._resolved_build_requirements = value

  @property
  def full_name(self):
    return self.make_full_name_str(self.name, self.version)

  @property
  def tarball_filename(self):
    return '%s.tar.gz' % (self.full_name)

  def artifact_path(self, build_target):
    'Return the full path for an artifact made with this package info and the given build_target.'
    return path.join(build_target.build_name, self.tarball_filename)
  
  @classmethod
  def make_full_name_str(clazz, name, version):
    return '%s%s%s' % (name, clazz.NAME_DELIMITER, str(version))

  def __str__(self):
    part1 = self.full_name
    part2 = []
    if self.requirements:
      part2.append(requirement.requirement_list_to_string(self.requirements))
    if self.build_requirements:
      part2.append(requirement.requirement_list_to_string(self.build_requirements))
    if self.properties:
      part2.append(self.properties_to_string())
    part2 = self.STR_PROPERTIES_DELIMITER.join(part2)
    if part2:
      return '%s(%s)' % (part1, part2)
    else:
      return part1

  def properties_to_string(self):
    items = sorted(self.properties.items())
    return '; '.join([ '%s=%s' % (item[0], item[1]) for item in items ])

  def __eq__(self, other):
    if not package_descriptor.is_package_info(other):
      raise RuntimeError('Got %s instead of package' % (type(other)))
    return self.__dict__ == other.__dict__

  def __lt__(self, other):
    assert package_descriptor.is_package_info(other)
    name_rv = cmp(self.name, other.name)
    if name_rv < 0:
      return True
    version_rv = version.compare(self.version, other.version)
    if version_rv < 0:
      return True
    requirements_rv = cmp(self.requirements, other.requirements)
    if requirements_rv < 0:
      return True
    build_requirements_rv = cmp(self.build_requirements, other.build_requirements)
    if build_requirements_rv < 0:
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
      'build_requirements': [ req.to_string_colon_format() for req in self.build_requirements ],
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
    build_requirements = clazz.parse_requirements(d.get('build_requirements', None))
    properties = d.get('properties', {})
    return package_descriptor(str(d['name']), str(d['version']),
                              requirements = requirements,
                              properties = properties,
                              build_requirements = build_requirements)

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
      if requirement.is_requirement(dep):
        result.append(dep)
      elif string_util.is_string(dep):
        reqs = psc.parse_requirement(dep).data
        result.extend(reqs)
      else:
        raise RuntimeError('Invalid requirement: %s - %s' % (str(dep), type(dep)))
    return result

  @classmethod
  def name_is_valid(clazz, name):
    if not string_util.is_string(name):
      return False
    if not name:
      return False
    return True

  @classmethod
  def is_package_info(clazz, o):
    return isinstance(o, package_descriptor)

  @classmethod
  def is_package_info_list(clazz, o):
    return object_util.is_homogeneous(o, package_descriptor)

  def export_compilation_flags_requirements(self, system):
    config = self.properties.get('export_compilation_flags_requirements', [])
    resolved = psc.resolve_list(config, system)
    deps_names = [ dep.name for dep in self.requirements ]
    export_names = resolved
    if export_names == dependency_resolver.ALL_DEPS:
      export_names = deps_names
    delta = (set(export_names) - set(deps_names))
    if delta:
      raise RuntimeError('Trying to export deps that are not specified by %s: %s' % (self.name, ' '.join(delta)))
    return export_names

  def extra_cflags(self, system):
    config = self.properties.get('extra_cflags', [])
    return psc.resolve_list(config, system)
      
  @property
  def env_vars(self):
    return self.properties.get(self.PROPERTY_ENV_VARS, {})

  @property
  def category(self):
    return self.properties.get(self.PROPERTY_CATEGORY, None)

  @property
  def pkg_config_name(self):
    'Return the name of the .pc file for pkg config this package uses.'
    return object_util.listify(self.properties.get(self.PROPERTY_PKG_CONFIG_NAME, [ self.name ]))

  def is_tool(self):
    return self.category == Category.TOOL

  @property
  def disabled(self):
    return self.properties.get(self.PROPERTY_DISABLED, False)

  @classmethod
  def full_name_cmp(clazz, pi1, pi2):
    'Compare name, version and revision and return an int either -1, 0, or 1'
    assert clazz.is_package_info(pi1)
    assert clazz.is_package_info(pi2)
    name_cmp = cmp(pi1.name, pi2.name)
    if name_cmp != 0:
      return name_cmp
    return version.compare(pi1.version, pi2.version)

  @property
  def requirements_names(self):
    return set([ req.name for req in self.requirements ])

  @property
  def build_requirements_names(self):
    return set([ req.name for req in self.build_requirements ])
