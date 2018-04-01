#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from collections import namedtuple
from bes.common import check
from rebuild.base import build_target, package_descriptor, requirement_list

class new_package_db_entry(namedtuple('new_package_db_entry', 'format_version,filename,checksum,name,version,system,level,arch,distro,requirements,properties,files')):

  def __new__(clazz, filename, checksum, name, version, system, level, arch, distro, requirements, properties, files):
    if filename:
      check.check_string(filename)
    if checksum:
      check.check_string(checksum)
    check.check_string(name)
    check.check_string(version)
    check.check_string(system)
    check.check_string(level)
    check.check_string(arch)
    if distro:
      check.check_string(distro)
    check.check_requirement_list(requirements)
    check.check_dict(properties)
    check.check_string_seq(files)
    return clazz.__bases__[0].__new__(clazz, 2, filename, checksum, name, version, system, level, arch, distro, requirements, properties, files)

  @property
  def descriptor(self):
    return package_descriptor(self.name, self.version, properties = self.properties, requirements = self.requirements)

  @property
  def build_target(self):
    return build_target(system = self.system, level = self.level, archs = [ self.arch ], distro = self.distro)
    
  def to_json(self):
    d = {
      '_format_version': self.format_version,
      'filename': self.filename,
      'checksum': self.checksum,
      'name': self.name,
      'version': self.version,
      'system': self.system,
      'level': self.level,
      'arch': self.arch,
      'distro': self.distro,
      'requirements': [ str(r) for r in self.requirements ],
      'properties': self.properties,
      'files': [ f for f in self.files ],
    }
    return json.dumps(d, indent = 2, sort_keys = True)

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
    return clazz('',
                 '',
                 descriptor.name,
                 str(descriptor.version),
                 '',
                 '',
                 '',
                 None,
                 descriptor.requirements,
                 descriptor.properties,
                 o['files'])
  
  @classmethod
  def _parse_json_v2(clazz, o):
    return clazz(o['filename'],
                 o['checksum'],
                 o['name'],
                 o['version'],
                 o['system'],
                 o['level'],
                 o['arch'],
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

