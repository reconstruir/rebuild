#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from collections import namedtuple
from bes.system.check import check
from bes.common.json_util import json_util
from bes.common.string_util import string_util
from bes.property.cached_property import cached_property
from bes.build.build_version import build_version
from bes.build.package_descriptor import package_descriptor
from bes.build.requirement import requirement
from bes.build.requirement_list import requirement_list
from .package_manifest import package_manifest

class package_db_entry(namedtuple('package_db_entry', 'format_version,name,version,revision,epoch,requirements,properties,manifest')):

  def __new__(clazz, name, version, revision, epoch, requirements, properties, manifest):
    check.check_string(name)
    check.check_string(version)
    check.check_int(revision)
    check.check_int(epoch)
    check.check_requirement_list(requirements)
    check.check_dict(properties)
    check.check_package_manifest(manifest)
    return clazz.__bases__[0].__new__(clazz, 2, name, version, revision, epoch, requirements, properties, manifest)

  def __hash__(self):
    return hash(self.to_json())
  
  @cached_property
  def build_version(self):
    return build_version(self.version, self.revision, self.epoch)
  
  @cached_property
  def descriptor(self):
    return package_descriptor(self.name, str(self.build_version), properties = self.properties, requirements = self.requirements)

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
    return clazz(o['name'],
                 o['version'],
                 o['revision'],
                 o['epoch'],
                 requirement_list.from_string_list(o['requirements']),
                 o['properties'],
                 package_manifest.parse_dict(o['manifest']))
  
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
      'requirements': self.requirements.to_string_list(),
      'properties': self.properties,
      'manifest': self.manifest.to_simple_dict(),
    }
  
check.register_class(package_db_entry, include_seq = False)
