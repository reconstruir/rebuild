#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from bes.fs import file_check
from bes.common import check, string_util
from bes.sqlite import sqlite
from rebuild.base import package_descriptor,  package_descriptor_list, build_version

from .artifact_descriptor import artifact_descriptor
from .artifact_descriptor_list import artifact_descriptor_list
from .db_error import *
from .files_db import files_db
from .package_files import package_files
from .package_metadata import package_metadata
from .package_metadata_list import package_metadata_list
from .util import util

class artifact_db(object):

  SCHEMA_ARTIFACTS = '''
create table artifacts(
  id                  integer primary key not null,
  name                text not null, 
  filename            text not null, 
  files_checksum      text not null, 
  env_files_checksum  text not null, 
  version             text not null, 
  revision            integer not null, 
  epoch               integer not null, 
  system              text not null, 
  level               text not null, 
  archs               text not null, 
  distro              text, 
  requirements        text,
  properties          text
);
'''

  def __init__(self, filename):
    self._filename = path.abspath(filename)
    self._db = sqlite(self._filename)
    self._db.ensure_table('artifacts', self.SCHEMA_ARTIFACTS)
    self._files_db = files_db(self._db)
    
  @property
  def filename(self):
    return self._filename

  def has_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    sql = 'select count(name) from artifacts where {}'.format(adesc.WHERE_EXPRESSION)
    t = adesc.to_sql_tuple()
    row = self._db.select_one(sql, adesc.to_sql_tuple())
    return row[0] > 0
  
  def add_artifact(self, md):
    check.check_package_metadata(md)
    adesc = md.artifact_descriptor
    if self.has_artifact(adesc):
      raise AlreadyInstalledError('Already installed: %s' % (str(adesc)), adesc)
    self._add_artifact_i(md)
    self._db.commit()

  def _add_artifact_i(self, md):
    keys, values = self._metadata_to_sql_keys_and_values(md)
    self._db.execute('insert into artifacts(%s) values(%s)' % (keys, values))
    files_table_name = md.artifact_descriptor.sql_table_name
    self._files_db.add_table(files_table_name, md.files.files)
    self._files_db.add_table(self._make_env_files_table_name(files_table_name), md.files.env_files)

  def replace_artifact(self, md):
    check.check_package_metadata(md)
    adesc = md.artifact_descriptor
    if not self.has_artifact(adesc):
      raise NotInstalledError('Not installed: %s' % (str(adesc)), adesc)
    self._remove_artifact(md.artifact_descriptor)
    self._add_artifact_i(md)
    self._db.commit()
    
  @classmethod
  def _metadata_to_sql_keys_and_values(self, md):
    d =  {
      'name': util.sql_encode_string(md.name),
      'filename': util.sql_encode_string(md.filename),
      'version': util.sql_encode_string(md.version),
      'revision': str(md.revision),
      'epoch': str(md.epoch),
      'system': util.sql_encode_string(md.system),
      'level': util.sql_encode_string(md.level),
      'archs': util.sql_encode_string_list(md.archs),
      'distro': util.sql_encode_string(md.distro),
      'requirements': util.sql_encode_requirements(md.requirements),
      'properties': util.sql_encode_dict(md.properties),
      'files_checksum': util.sql_encode_string(md.files.files_checksum),
      'env_files_checksum': util.sql_encode_string(md.files.env_files_checksum),
    }
    keys = ', '.join(d.keys())
    values = ', '.join(d.values())
    return keys, values
    
  @classmethod
  def _make_env_files_table_name(clazz, name):
    return name + '_env'
    
  def remove_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    if not self.has_artifact(adesc):
      raise NotInstalledError('Not installed: %s' % (str(adesc)), adesc)
    self._remove_artifact(adesc)
    self._db.commit()

  def _remove_artifact(self, adesc):
    sql = 'delete from artifacts where {}'.format(adesc.WHERE_EXPRESSION)
    self._db.execute(sql, adesc.to_sql_tuple())
    files_table_name = adesc.sql_table_name
    self._files_db.remove_table(files_table_name)
    self._files_db.remove_table(self._make_env_files_table_name(files_table_name))

  @classmethod
  def _build_target_to_sql_tuple(clazz, bt):
    return ( bt.system, bt.level, util.sql_encode_string_list(bt.archs, quoted = False) )
  
  def list_all_by_descriptor(self, build_target = None):
    if build_target:
      sql = '''select name, version, revision, epoch, system, level, archs, distro from artifacts where system=? and level=? and archs=? order by name asc, version asc, revision asc, epoch asc, system asc, level asc, archs asc, distro asc'''
      data = self._build_target_to_sql_tuple(build_target)
    else:
      sql = '''select name, version, revision, epoch, system, level, archs, distro from artifacts order by name asc, version asc, revision asc, epoch asc, system asc, level asc, archs asc, distro asc'''
      data = ()
    rows = self._db.select_namedtuples(sql, data)
    values = [ self._load_row_to_artifact_descriptor(row) for row in rows ]
    return artifact_descriptor_list(values = values)
  
  def list_all_by_metadata(self, build_target = None):
    if build_target:
      sql = '''select * from artifacts where system=? and level=? and archs=? order by name asc, version asc, revision asc, epoch asc, system asc, level asc, archs asc, distro asc'''
      data = self._build_target_to_sql_tuple(build_target)
    else:
      sql = '''select * from artifacts order by name asc, version asc, revision asc, epoch asc, system asc, level asc, archs asc, distro asc'''
      data = ()
    rows = self._db.select_namedtuples(sql, data)
    if not rows:
      return package_metadata_list()
    values = [ self._load_row_to_package_metadata(row) for row in rows ]
    return package_metadata_list(values = values)

  def list_all_by_package_descriptor(self, build_target = None):
    if build_target:
      sql = '''select name, version, revision, epoch, properties, requirements from artifacts where system=? and level=? and archs=? order by name asc, version asc, revision asc, epoch asc'''
      data = self._build_target_to_sql_tuple(build_target)
    else:
      sql = '''select name, version, revision, epoch, properties, requirements from artifacts order by name asc, version asc, revision asc, epoch asc'''
      data = ()
    rows = self._db.select_namedtuples(sql, data)
    if not rows:
      return package_descriptor_list()
    values = [ self._load_row_to_package_descriptor(row) for row in rows ]
    return package_descriptor_list(values = values)

  @classmethod
  def _load_row_to_artifact_descriptor(clazz, row):
    assert row
    return artifact_descriptor(row.name,
                               row.version,
                               row.revision,
                               row.epoch,
                               row.system,
                               row.level,
                               json.loads(row.archs),
                               row.distro)
  
  def _load_artifact(self, adesc):
    sql = 'select * from artifacts where {}'.format(adesc.WHERE_EXPRESSION)
    rows = self._db.select_namedtuples(sql, adesc.to_sql_tuple())
    if not rows:
      return None
    assert(len(rows) == 1)
    md = self._load_row_to_package_metadata(rows[0], adesc = adesc)
    return md
  
  def _load_row_to_package_metadata(self, row, adesc = None):
    assert row
    adesc = adesc or self._load_row_to_artifact_descriptor(row)
    files_table_name = adesc.sql_table_name
    files = package_files(self._files_db.file_checksums(files_table_name),
                          self._files_db.file_checksums(self._make_env_files_table_name(files_table_name)),
                          row.files_checksum,
                          row.env_files_checksum)
    md =  package_metadata(row.filename,
                           row.name,
                           row.version,
                           row.revision,
                           row.epoch,
                           row.system,
                           row.level,
                           json.loads(row.archs),
                           row.distro,
                           util.sql_decode_requirements(row.requirements),
                           json.loads(row.properties),
                           files)
    return md
  
  def _load_row_to_package_descriptor(self, row):
    assert row
    return package_descriptor(row.name,
                              build_version(row.version, row.revision, row.epoch),
                              json.loads(row.properties),
                              util.sql_decode_requirements(row.requirements))
  
  def find_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    return self._load_artifact(adesc)

  def get_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    md = self._load_artifact(adesc)
    if not md:
      raise NotInstalledError('Not installed: %s' % (str(adesc)), adesc)
    return md
