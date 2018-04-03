#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#import json, pickle
#from collections import namedtuple
#from bes.fs import file_checksum_list
from bes.common import check, json_util, string_util
#from rebuild.base import build_target, build_version, package_descriptor, requirement_list
from rebuild.base import requirement_list

class util(object):

  @classmethod
  def requirements_from_string_list(clazz, l):
    check.check_string_seq(l)
    result = requirement_list()
    for n in l:
      result.extend(requirement_list.parse(n))
    return result

  @classmethod
  def requirements_to_string_list(clazz, reqs):
    check.check_requirement_list(reqs)
    return [ str(r) for r in reqs ]

  @classmethod
  def sql_encode_string(clazz, s):
    return string_util.quote(s or '', quote_char = "'")

  @classmethod
  def sql_encode_string_list(clazz, l):
    return clazz.sql_encode_string(json_util.to_json(l))
  
  @classmethod
  def sql_encode_requirements(clazz, reqs):
    return clazz.sql_encode_string_list(clazz.requirements_to_string_list(reqs))

  @classmethod
  def sql_decode_requirements(clazz, text):
    return clazz.requirements_from_string_list(json.loads(text))
  
  @classmethod
  def sql_encode_dict(clazz, d):
    return clazz.sql_encode_string(json_util.to_json(d, sort_keys = True))

  @classmethod
  def sql_encode_files(clazz, files):
    return clazz.sql_encode_string(json_util.to_json(files.to_simple_list()))

'''
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
      'requirements': [ str(r) for r in self.requirements ],
      'properties': self.properties,
      'files': self.files.to_simple_list(),
    }
  
  def to_sql_dict(self):
    'Return a dict suitable to use directly with sqlite insert commands'
    d =  {
      'name': string_util.quote(self.name, "'"),
      'filename': string_util.quote(self.filename, "'"),
      'checksum': string_util.quote(self.checksum, "'"),
      'version': string_util.quote(self.version, "'"),
      'revision': str(self.revision),
      'epoch': str(self.epoch),
      'system': string_util.quote(self.system, "'"),
      'level': string_util.quote(self.level, "'"),
      'archs': string_util.quote(json_util.to_json(self.archs, sort_keys = True), "'"),
      'distro': string_util.quote(self.distro or '', "'"),
      'requirements': string_util.quote(json_util.to_json([ str(r) for r in self.requirements ], sort_keys = True), "'"),
      'properties': string_util.quote(json_util.to_json(self.properties, sort_keys = True), "'"),
      'files': string_util.quote(json_util.to_json(self.files.to_simple_list()), "'"),
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
                 clazz._requirements_from_string_list(json.loads(row.requirements)),
                 json.loads(row.properties),
                 file_checksum_list.from_json(row.files))
'''
