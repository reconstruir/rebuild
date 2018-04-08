#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from collections import namedtuple
from bes.fs import file_checksum, file_checksum_list
from bes.common import cached_property, check, json_util, string_util
from rebuild.base import build_version, package_descriptor, requirement_list
from .util import util

class package_db_entry(namedtuple('package_db_entry', 'format_version,name,version,revision,epoch,requirements,properties,files,checksum')):

  def __new__(clazz, name, version, revision, epoch, requirements, properties, files, checksum = None):
    check.check_string(name)
    check.check_string(version)
    check.check_int(revision)
    check.check_int(epoch)
    check.check_requirement_list(requirements)
    check.check_dict(properties)
    files = files or file_checksum_list()
    check.check_file_checksum_list(files)
    if checksum:
      check.check_string(checksum)
    checksum = checksum or files.checksum()
    return clazz.__bases__[0].__new__(clazz, 2, name, version, revision, epoch, requirements, properties, files, checksum)

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
                 util.requirements_from_string_list(o['requirements']),
                 o['properties'],
                 file_checksum_list.from_simple_list(o['files']),
                 o['checksum'])
  
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
      'requirements': util.requirements_to_string_list(self.requirements),
      'properties': self.properties,
      'files': self.files.to_simple_list(),
      'checksum': self.checksum,
    }
  
  def to_sql_dict(self):
    'Return a dict suitable to use directly with sqlite insert commands'
    d =  {
      'name': util.sql_encode_string(self.name),
      'version': util.sql_encode_string(self.version),
      'revision': str(self.revision),
      'epoch': str(self.epoch),
      'requirements': util.sql_encode_requirements(self.requirements),
      'properties': util.sql_encode_dict(self.properties),
      'checksum': util.sql_encode_string(self.checksum),
    }
    return d
  
check.register_class(package_db_entry, include_seq = False)
