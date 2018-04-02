#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, pickle
from collections import namedtuple
from bes.common import check, string_util
from rebuild.base import build_target, build_version, package_descriptor, requirement_list

class new_package_db_entry(namedtuple('new_package_db_entry', 'format_version,name,version,revision,epoch,system,level,archs,distro,requirements,properties,files')):

  def __new__(clazz, name, version, revision, epoch, system, level, archs, distro, requirements, properties, files):
    check.check_string(name)
    check.check_string(version)
    check.check_int(revision)
    check.check_int(epoch)
    check.check_string(system)
    check.check_string(level)
    check.check_string_seq(archs)
    if distro:
      check.check_string(distro)
    check.check_requirement_list(requirements)
    check.check_dict(properties)
    check.check_string_seq(files)
    return clazz.__bases__[0].__new__(clazz, 2, name, version, revision, epoch, system, level, archs, distro, requirements, properties, files)

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
    return json.dumps(self.to_simple_dict(), indent = 2, sort_keys = True)

  @classmethod
  def parse_json(clazz, text):
    o = json.loads(text)
    format_version = o.get('_format_version', 1)
    if format_version == 1:
      return clazz._parse_json_v1(o)
    elif format_version == 2:
      return clazz._parse_json_v2(o)
    else:
      raise ValueError('invalid format_version: %s' % (format_version))

  @classmethod
  def _parse_json_v1(clazz, o):
    if 'descriptor' in o:
      key = 'descriptor'
    else:
      key = 'info'
    assert key in o
    assert 'files' in o
    dd = o[key]
    check.check_dict(dd)
    descriptor = package_descriptor.parse_dict(dd)
    return clazz(descriptor.name,
                 descriptor.version.upstream_version,
                 descriptor.version.revision,
                 descriptor.version.epoch,
                 '',
                 '',
                 '',
                 None,
                 descriptor.requirements,
                 descriptor.properties,
                 o['files'])
  
  @classmethod
  def _parse_json_v2(clazz, o):
    return clazz(o['name'],
                 o['version'],
                 o['revision'],
                 o['epoch'],
                 o['system'],
                 o['level'],
                 o['archs'],
                 o['distro'],
                 clazz._parse_requirements(o['requirements']),
                 o['properties'],
                 o['files'])
  
  @classmethod
  def _parse_requirements(clazz, l):
    check.check_string_seq(l)
    reqs = requirement_list()
    for n in l:
      reqs.extend(requirement_list.parse(n))
    return reqs

  def to_simple_dict(self):
    'Return a simplified dict suitable for json encoding.'
    return {
      '_format_version': self.format_version,
      'name': self.name,
      'version': self.version,
      'revision': self.revision,
      'epoch': self.epoch,
      'system': self.system,
      'level': self.level,
      'archs': self.archs,
      'distro': self.distro,
      'requirements': [ str(r) for r in self.requirements ],
      'properties': self.properties,
      'files': [ f for f in self.files ],
    }
  
  def to_sql_dict(self):
    'Return a dict suitable to use directly with sqlite insert commands'
    d =  {
      'name': string_util.quote(self.name, "'"),
      'version': string_util.quote(self.version, "'"),
      'revision': str(self.revision),
      'epoch': str(self.epoch),
      'system': string_util.quote(self.system, "'"),
      'level': string_util.quote(self.level, "'"),
      'archs': string_util.quote(json.dumps(self.archs), "'"),
      'distro': string_util.quote(self.distro or '', "'"),
      'requirements': string_util.quote(json.dumps([ str(r) for r in self.requirements ]), "'"),
      'properties': string_util.quote(json.dumps(self.properties), "'"),
      'files': string_util.quote(json.dumps([ f for f in self.files ]), "'"),
    }
    return d
  
  @classmethod
  def from_sql_row(clazz, row):
    check.check_tuple(row)
    return clazz(row.name,
                 row.version,
                 row.revision,
                 row.epoch,
                 row.system,
                 row.level,
                 json.loads(row.archs),
                 row.distro or None,
                 clazz._parse_requirements(json.loads(row.requirements)),
                 json.loads(row.properties),
                 json.loads(row.files))

check.register_class(new_package_db_entry, include_seq = False)
