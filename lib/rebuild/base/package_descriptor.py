#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from bes.common import check, object_util, string_util
from bes.compat import cmp

from .build_category import build_category
from .build_system import build_system
from .build_version import build_version
from .reitred_masked_config import reitred_masked_config
from .requirement import requirement
from .requirement_list import requirement_list

class package_descriptor(object):

  NAME_DELIMITER = '-'

  STR_PROPERTIES_DELIMITER = '; '

  PROPERTY_CATEGORY = 'category'
  PROPERTY_PKG_CONFIG_NAME = 'pkg_config_name'
  
  def __init__(self, name, version, requirements = None, build_tool_requirements = None, build_requirements = None, properties = None):
    check.check_string(name)
#    check.check_build_version(version)
    requirements = requirement_list(requirements)
    check.check_requirement_list(requirements)

    build_tool_requirements = requirement_list(build_tool_requirements)
    check.check_requirement_list(build_tool_requirements)

    build_requirements = requirement_list(build_requirements)
    check.check_requirement_list(build_requirements)

    properties = properties or {}

    if not self.name_is_valid(name):
      raise RuntimeError('Invalid name: \"%s\"' % (name))
    self._name = name
    self._version = build_version.validate_version(version)

    self._requirements = self.parse_requirements(requirements)
    self._resolved_requirements = None

    self._build_tool_requirements = self.parse_requirements(build_tool_requirements)
    self._resolved_build_tool_requirements = None

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
  def build_tool_requirements(self):
    return self._build_tool_requirements

  @build_tool_requirements.setter
  def build_tool_requirements(self, value):
    raise RuntimeError('build_tool_requirements are immutable.')

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
    check.check_package_descriptor_seq(value)
    self._resolved_requirements = value

  @property
  def resolved_build_tool_requirements(self):
    return self._resolved_build_tool_requirements or []

  @resolved_build_tool_requirements.setter
  def resolved_build_tool_requirements(self, value):
    if self._resolved_build_tool_requirements != None:
      raise RuntimeError('resolved_build_tool_requirements can only be set once')
    check.check_package_descriptor_seq(value)
    self._resolved_build_tool_requirements = value

  @property
  def resolved_build_requirements(self):
    return self._resolved_build_requirements or []

  @resolved_build_requirements.setter
  def resolved_build_requirements(self, value):
    if self._resolved_build_requirements != None:
      raise RuntimeError('resolved_build_requirements can only be set once')
    check.check_package_descriptor_seq(value)
    self._resolved_build_requirements = value

  @property
  def full_name(self):
    return self.make_full_name_str(self.name, self.version)

  @property
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
    if self.build_tool_requirements:
      part2.append(self.build_tool_requirements.to_string())
    if self.build_requirements:
      part2.append(self.build_requirements.to_string())
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
    check.check_package_descriptor(other)
    return self.__dict__ == other.__dict__

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
    build_tool_requirements_rv = cmp(self.build_tool_requirements, other.build_tool_requirements)
    if build_tool_requirements_rv < 0:
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
      'build_tool_requirements': [ req.to_string_colon_format() for req in self.build_tool_requirements ],
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
    build_tool_requirements = clazz.parse_requirements(d.get('build_tool_requirements', None))
    build_requirements = clazz.parse_requirements(d.get('build_requirements', None))
    properties = d.get('properties', {})
    return package_descriptor(str(d['name']), str(d['version']),
                              requirements = requirements,
                              build_tool_requirements = build_tool_requirements,
                              build_requirements = build_requirements,
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
        reqs = reitred_masked_config.parse_requirement(dep).data
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
    config = self.properties.get('extra_cflags', [])
    return reitred_masked_config.resolve_list(config, system)
      
  @property
  def env_vars(self):
    return self.properties.get('env_vars', {})

  @property
  def category(self):
    return self.properties.get(self.PROPERTY_CATEGORY, None)

  @property
  def pkg_config_name(self):
    'Return the name of the .pc file for pkg config this package uses.'
    return object_util.listify(self.properties.get(self.PROPERTY_PKG_CONFIG_NAME, [ self.name ]))

  def is_tool(self):
    return self.category.lower() == build_category.value_to_name(build_category.TOOL).lower()

  @classmethod
  def full_name_cmp(clazz, pi1, pi2):
    'Compare name, version and revision and return an int either -1, 0, or 1'
    check.check_package_descriptor(pi1)
    check.check_package_descriptor(pi2)
    name_cmp = cmp(pi1.name, pi2.name)
    if name_cmp != 0:
      return name_cmp
    return build_version.compare(pi1.version, pi2.version)

  @property
  def requirements_names(self):
    return set([ req.name for req in self.requirements ])

  @property
  def build_tool_requirements_names(self):
    return set([ req.name for req in self.build_tool_requirements ])

  @property
  def build_requirements_names(self):
    return set([ req.name for req in self.build_requirements ])

  @property
  def resolved_requirements_names(self):
    return set([ req.name for req in self.resolved_requirements ])

  @property
  def resolved_build_tool_requirements_names(self):
    return set([ req.name for req in self.resolved_build_tool_requirements ])
  
  @property
  def resolved_build_requirements_names(self):
    return set([ req.name for req in self.resolved_build_requirements ])
  
  def requirements_for_system(self, system):
    return [ req for req in self.requirements if build_system.mask_matches(req.system_mask, system) ]

  def requirements_names_for_system(self, system):
    return set([ req.name for req in self.requirements_for_system(system) ])
  
  def build_tool_requirements_for_system(self, system):
    return [ req for req in self.build_tool_requirements if build_system.mask_matches(req.system_mask, system) ]

  def build_tool_requirements_names_for_system(self, system):
    return set([ req.name for req in self.build_tool_requirements_for_system(system) ])

  def build_requirements_for_system(self, system):
    return [ req for req in self.build_requirements if build_system.mask_matches(req.system_mask, system) ]

  def build_requirements_names_for_system(self, system):
    return set([ req.name for req in self.build_requirements_for_system(system) ])

check.register_class(package_descriptor)
