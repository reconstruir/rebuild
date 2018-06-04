#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from collections import namedtuple
from bes.common import cached_property, check, json_util, string_util
from rebuild.base import build_target, build_version, package_descriptor, requirement_list

from .artifact_descriptor import artifact_descriptor
from .package_files import package_files
from .util import util

class package_metadata(namedtuple('package_metadata', 'format_version, filename, name, version, revision, epoch, system, level, archs, distro, requirements, properties, files')):

  def __new__(clazz, filename, name, version, revision, epoch, system, level, archs, distro, requirements, properties, files):
    check.check_string(filename)
    check.check_string(name)
    check.check_string(version)
    check.check_int(revision)
    check.check_int(epoch)
    check.check_string(system)
    check.check_string(level)
    check.check_string_seq(archs)
    distro = distro or ''
    check.check_string(distro)
    if check.is_string(requirements):
      requirements = requirement_list.parse(requirements)
    requirements = requirements or requirement_list()
    check.check_requirement_list(requirements)
    properties = properties or {}
    check.check_dict(properties)
    check.check_package_files(files)
    return clazz.__bases__[0].__new__(clazz, 2, filename, name, version, revision, epoch, system, level, archs, distro, requirements, properties, files)

  @cached_property
  def build_version(self):
    return build_version(self.version, self.revision, self.epoch)
  
  @cached_property
  def package_descriptor(self):
    return package_descriptor(self.name, str(self.build_version), properties = self.properties, requirements = self.requirements)

  @cached_property
  def artifact_descriptor(self):
    return artifact_descriptor(self.name, self.version, self.revision, self.epoch, self.system, self.level, self.archs, self.distro)

  @cached_property
  def build_target(self):
    return build_target(system = self.system, level = self.level, archs = self.archs, distro = self.distro)
    
  def to_json(self):
    return json_util.to_json(self.to_simple_dict(), indent = 2, sort_keys = True)

  @classmethod
  def parse_json(clazz, text):
    o = json.loads(text)
    format_version = o.get('_format_version', 1)
    if format_version == 2:
      return clazz._parse_dict_v2(o)
    else:
      raise ValueError('invalid format_version: %s' % (format_version))

  @classmethod
  def _parse_dict_v2(clazz, o):
    return clazz(o['filename'],
                 o['name'],
                 o['version'],
                 o['revision'],
                 o['epoch'],
                 o['system'],
                 o['level'],
                 o['archs'],
                 o['distro'],
                 util.requirements_from_string_list(o['requirements']),
                 o['properties'],
                 package_files.parse_dict(o['files']))
  
  def to_simple_dict(self):
    'Return a simplified dict suitable for json encoding.'
    return {
      '_format_version': self.format_version,
      'name': self.name,
      'filename': self.filename,
      'version': self.version,
      'revision': self.revision,
      'epoch': self.epoch,
      'system': self.system,
      'level': self.level,
      'archs': self.archs,
      'distro': self.distro,
      'requirements': util.requirements_to_string_list(self.requirements),
      'properties': self.properties,
      'files': self.files.to_simple_dict(),
    }

  def clone_with_filename(self, filename):
    l = list(self)
    l[1] = filename
    # remove format version which __init__() does not take
    l.pop(0)
    return self.__class__(*l)

  @property
  def full_name(self):
    return self.make_full_name_str(self.name, self.build_version)

  @classmethod
  def make_full_name_str(clazz, name, version):
    return '%s%s%s' % (name, '-', str(version))
  
check.register_class(package_metadata, include_seq = False)
