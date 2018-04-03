#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from collections import namedtuple
from bes.fs import file_checksum_list
from bes.common import check, json_util, string_util
from rebuild.base import build_target, build_version, package_descriptor, requirement_list
from .util import util

class package_metadata(namedtuple('package_metadata', 'format_version, filename, checksum, name, version, revision, epoch, system, level, archs, distro, requirements, properties, files')):

  def __new__(clazz, filename, checksum, name, version, revision, epoch, system, level, archs, distro, requirements, properties, files):
    check.check_string(filename)
    check.check_string(checksum)
    check.check_string(name)
    check.check_string(version)
    check.check_int(revision)
    check.check_int(epoch)
    check.check_string(system)
    check.check_string(level)
    check.check_string_seq(archs)
    if distro:
      check.check_string(distro)
    if check.is_string(requirements):
      requirements = requirement_list.parse(requirements)
    requirements = requirements or requirement_list()
    check.check_requirement_list(requirements)
    properties = properties or {}
    check.check_dict(properties)
    files = files or file_checksum_list()
    check.check_file_checksum_list(files)
    return clazz.__bases__[0].__new__(clazz, 2, filename, checksum, name, version, revision, epoch, system, level, archs, distro, requirements, properties, files)

  @property
  def build_version(self):
    return build_version(self.version, self.revision, self.epoch)
  
  @property
  def descriptor(self):
    return package_descriptor(self.name, str(self.build_version), properties = self.properties, requirements = self.requirements)

  @property
  def build_target(self):
    return build_target(system = self.system, level = self.level, archs = self.archs, distro = self.distro)
    
  def to_json(self):
    return json_util.to_json(self.to_simple_dict(), indent = 2, sort_keys = True)

  @classmethod
  def parse_json(clazz, text):
    o = json.loads(text)
    format_version = o.get('_format_version', 1)
    if format_version == 1:
      return clazz._parse_dict_v1(o)
    elif format_version == 2:
      return clazz._parse_dict_v2(o)
    else:
      raise ValueError('invalid format_version: %s' % (format_version))

  @classmethod
  def _parse_dict_v1(clazz, o):
    version = build_version.parse(o['version'])
    return clazz('',
                 '',
                 o['name'],
                 version.upstream_version,
                 version.revision,
                 version.epoch,
                 o['system'],
                 o['level'],
                 o['archs'],
                 o['distro'],
                 util.requirements_from_string_list(o['requirements']),
                 o['properties'],
                 [])
  
  @classmethod
  def _parse_dict_v2(clazz, o):
    return clazz(o['filename'],
                 o['checksum'],
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
                 file_checksum_list.from_simple_list(o['files']))
  
  def to_simple_dict(self):
    'Return a simplified dict suitable for json encoding.'
    return {
      '_format_version': self.format_version,
      'name': self.name,
      'filename': self.filename,
      'checksum': self.checksum,
      'version': self.version,
      'revision': self.revision,
      'epoch': self.epoch,
      'system': self.system,
      'level': self.level,
      'archs': self.archs,
      'distro': self.distro,
      'requirements': util.requirements_to_string_list(self.requirements),
      'properties': self.properties,
      'files': self.files.to_simple_list(),
    }
  
  def to_sql_dict(self):
    'Return a dict suitable to use directly with sqlite insert commands'
    d =  {
      'name': util.sql_encode_string(self.name),
      'filename': util.sql_encode_string(self.filename),
      'checksum': util.sql_encode_string(self.checksum),
      'version': util.sql_encode_string(self.version),
      'revision': str(self.revision),
      'epoch': str(self.epoch),
      'system': util.sql_encode_string(self.system),
      'level': util.sql_encode_string(self.level),
      'archs': sql_encode_string_list(self.archs),
      'distro': util.sql_encode_string(self.distro),
      'requirements': sql_encode_requirements(self.requirements),
      'properties': sql_encode_dict(self.properties),
      'files': sql_encode_files(self.files),
    }
    return d
  
  @classmethod
  def from_sql_row(clazz, row):
    check.check_tuple(row)
    return clazz(row.filename,
                 row.checksum,
                 row.name,
                 row.version,
                 row.revision,
                 row.epoch,
                 row.system,
                 row.level,
                 json.loads(row.archs),
                 row.distro or None,
                 util.sql_decode_requirements(row.requirements),
                 json.loads(row.properties),
                 file_checksum_list.from_json(row.files))

check.register_class(package_metadata, include_seq = False)
