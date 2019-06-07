#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from bes.system.log import log
from bes.fs import file_check
from bes.common.check import check
from bes.common.string_util import string_util
from bes.sqlite.sqlite import sqlite
from rebuild.base import artifact_descriptor, artifact_descriptor_list, package_descriptor,  package_descriptor_list, build_target, build_version

from .db_error import *
from .files_db import files_db
from .package_manifest import package_manifest
from .package_metadata import package_metadata
from .package_metadata_list import package_metadata_list
from .sql_encoding import sql_encoding

class artifact_db(object):

  SCHEMA_ARTIFACTS = '''
create table artifacts(
  id                   integer primary key not null,
  name                 text not null, 
  filename             text not null, 
  contents_checksum    text not null, 
  version              text not null, 
  revision             integer not null, 
  epoch                integer not null, 
  system               text not null, 
  level                text not null, 
  arch                 text not null, 
  distro               text, 
  distro_version_major text, 
  distro_version_minor text, 
  requirements         text,
  properties           text
);
'''

  def __init__(self, filename):
    log.add_logging(self, 'artifact_db')
#    log.configure('artifact_db=debug format=brief')
    self._filename = path.abspath(filename)
    self._db = sqlite(self._filename)
    self._db.ensure_table('artifacts', self.SCHEMA_ARTIFACTS)
    self._files_db = files_db(self._db)
    self._db.create_function('rebuild_build_target_matches', 12, self._build_target_matches)

  @staticmethod
  def _build_target_matches(system, distro, distro_version_major, distro_version_minor, arch, level,
                            wanted_system, wanted_distro, wanted_distro_version_major, wanted_distro_version_minor, wanted_arch, wanted_level):
    actual = build_target(system, distro,
                          distro_version_major, distro_version_minor,
                          sql_encoding.decode_arch(arch),
                          level)
    wanted = build_target(wanted_system, wanted_distro,
                          wanted_distro_version_major, wanted_distro_version_minor,
                          sql_encoding.decode_arch(wanted_arch),
                          wanted_level)
    return wanted.match(actual)
      
  @property
  def filename(self):
    return self._filename

  WHERE_EXPRESSION = '\
name=? and \
version=? and \
revision=? and \
epoch=? and \
rebuild_build_target_matches(system, distro, distro_version_major, distro_version_minor, arch, level, ?, ?, ?, ?, ?, ?)'

  def has_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    sql = 'select count(name) from artifacts where {}'.format(self.WHERE_EXPRESSION)
    row = self._db.select_one(sql, adesc.sql_tuple)
    return row[0] > 0
  
  def add_artifact(self, md):
    check.check_package_metadata(md)
    adesc = md.artifact_descriptor
    if self.has_artifact(adesc):
      raise AlreadyInstalledError('Already installed: %s' % (str(adesc)), adesc)
    self.log_d('add_artifact: adesc=%s' % (str(adesc)))
    self._db.begin()
    self._add_artifact_i(md)
    self._db.commit()

  def _add_artifact_i(self, md):
    keys, values = self._metadata_to_sql_keys_and_values(md)

    self._db.execute('insert into artifacts(%s) values(%s)' % (keys, values))
    files_table_name = md.artifact_descriptor.sql_table_name
    self._files_db.add_table(files_table_name, md.manifest.files)
    self._files_db.add_table(self._make_env_files_table_name(files_table_name), md.manifest.env_files)

  def replace_artifact(self, md):
    check.check_package_metadata(md)
    adesc = md.artifact_descriptor
    if not self.has_artifact(adesc):
      raise NotInstalledError('Not installed: %s' % (str(adesc)), adesc)
    self._db.begin()
    self._remove_artifact_i(md.artifact_descriptor)
    self._add_artifact_i(md)
    self._db.commit()

  def add_or_replace_artifact(self, md):
    check.check_package_metadata(md)
    adesc = md.artifact_descriptor
    self._db.begin()
    self.log_d('add_or_replace_artifact(adesc=%s)' % (str(adesc)))
    if not self.has_artifact(adesc):
      self._add_artifact_i(md)
    else:
      self._remove_artifact_i(md.artifact_descriptor)
      self._add_artifact_i(md)
    self._db.commit()
    
  @classmethod
  def _metadata_to_sql_keys_and_values(self, md):
#    if md.distro_version_minor in [ None, '', 'none' ]:
#      distro_version_minor = None
#    else:
#      distro_version_minor = sql_encoding.encode_string(md.distro_version_minor)

    d =  {
      'name': sql_encoding.encode_string(md.name),
      'filename': sql_encoding.encode_string(md.filename),
      'version': sql_encoding.encode_string(md.version),
      'revision': str(md.revision),
      'epoch': str(md.epoch),
      'system': sql_encoding.encode_string(md.system),
      'level': sql_encoding.encode_string(md.level),
      'arch': sql_encoding.encode_string_list(md.arch),
      'distro': sql_encoding.encode_string(md.distro),
      'distro_version_major': sql_encoding.encode_string(md.distro_version_major),
      'distro_version_minor': sql_encoding.encode_string(md.distro_version_minor),
      'requirements': sql_encoding.encode_requirements(md.requirements),
      'properties': sql_encoding.encode_dict(md.properties),
      'contents_checksum': sql_encoding.encode_string(md.manifest.contents_checksum),
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
    self._db.begin()
    self._remove_artifact_i(adesc)
    self._db.commit()

  def _remove_artifact_i(self, adesc):
    sql = 'delete from artifacts where {}'.format(self.WHERE_EXPRESSION)
    self._db.execute(sql, adesc.sql_tuple)
    files_table_name = adesc.sql_table_name
    self._files_db.remove_table(files_table_name)
    self._files_db.remove_table(self._make_env_files_table_name(files_table_name))

  @classmethod
  def _build_target_to_sql_tuple(clazz, bt):
    return ( bt.system, bt.distro, bt.distro_version_major, bt.distro_version_minor or '', sql_encoding.encode_string_list(bt.arch, quoted = False), bt.level )
  
  def list_all_by_descriptor(self, build_target = None):
    if build_target:
      sql = '''\
select name, version, revision, epoch, system, level, arch, distro, distro_version_major, distro_version_minor from artifacts \
where rebuild_build_target_matches(system, distro, distro_version_major, distro_version_minor, arch, level, ?, ?, ?, ?, ?, ?) \
order by name asc, version asc, revision asc, epoch asc, system asc, level asc, arch asc, distro, distro_version_major, distro_version_minor asc'''
      data = self._build_target_to_sql_tuple(build_target)
    else:
      sql = '''select name, version, revision, epoch, system, level, arch, distro, distro_version_major, distro_version_minor from artifacts order by name asc, version asc, revision asc, epoch asc, system asc, level asc, arch asc, distro, distro_version_major, distro_version_minor asc'''
      data = ()
    rows = self._db.select_namedtuples(sql, data)
    values = [ self._load_row_to_artifact_descriptor(row) for row in rows ]
    values = sorted(values)
    return artifact_descriptor_list(values = values)
  
  def list_all_by_metadata(self, build_target = None):
    if build_target:
      sql = '''\
select * from artifacts \
where rebuild_build_target_matches(system, distro, distro_version_major, distro_version_minor, arch, level, ?, ?, ?, ?, ?, ?) \
order by name asc, version asc, revision asc, epoch asc, system asc, level asc, arch asc, distro, distro_version_major, distro_version_minor asc'''
      data = self._build_target_to_sql_tuple(build_target)
    else:
      sql = '''select * from artifacts order by name asc, version asc, revision asc, epoch asc, system asc, level asc, arch asc, distro, distro_version_major, distro_version_minor asc'''
      data = ()
    rows = self._db.select_namedtuples(sql, data)
    if not rows:
      return package_metadata_list()
    values = [ self._load_row_to_package_metadata(row) for row in rows ]
    values = sorted(values)
    return package_metadata_list(values = values)

  def list_all_by_package_descriptor(self, build_target = None):
    if build_target:
      sql = '''select name, version, revision, epoch, properties, requirements from artifacts \
where rebuild_build_target_matches(system, distro, distro_version_major, distro_version_minor, arch, level, ?, ?, ?, ?, ?, ?) \
order by name asc, version asc, revision asc, epoch asc'''
      data = self._build_target_to_sql_tuple(build_target)
    else:
      sql = '''select name, version, revision, epoch, properties, requirements from artifacts order by name asc, version asc, revision asc, epoch asc'''
      data = ()
    rows = self._db.select_namedtuples(sql, data)
    if not rows:
      return package_descriptor_list()
    values = [ self._load_row_to_package_descriptor(row) for row in rows ]
    values = sorted(values)
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
                               sql_encoding.decode_arch(row.arch),
                               row.distro,
                               row.distro_version_major,
                               row.distro_version_minor)
  
  def _load_artifact(self, adesc):
    sql = 'select * from artifacts where {}'.format(self.WHERE_EXPRESSION)
    rows = self._db.select_namedtuples(sql, adesc.sql_tuple)
    if not rows:
      return None
    assert(len(rows) == 1)
    md = self._load_row_to_package_metadata(rows[0])
    return md
  
  def _load_row_to_package_metadata(self, row):
    assert row
    adesc = self._load_row_to_artifact_descriptor(row)
    files_table_name = adesc.sql_table_name
    files = package_manifest(self._files_db.package_manifest(files_table_name),
                             self._files_db.package_manifest(self._make_env_files_table_name(files_table_name)),
                             row.contents_checksum)
    md =  package_metadata(package_metadata.FORMAT_VERSION,
                           row.filename,
                           row.name,
                           row.version,
                           row.revision,
                           row.epoch,
                           row.system,
                           row.level,
                           sql_encoding.decode_arch(row.arch),
                           row.distro,
                           row.distro_version_major,
                           row.distro_version_minor,
                           sql_encoding.decode_requirements(row.requirements),
                           json.loads(row.properties),
                           files)
    return md
  
  def _load_row_to_package_descriptor(self, row):
    assert row
    return package_descriptor(row.name,
                              build_version(row.version, row.revision, row.epoch),
                              properties = json.loads(row.properties),
                              requirements = sql_encoding.decode_requirements(row.requirements))
  
  def find_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    return self._load_artifact(adesc)

  def get_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    md = self._load_artifact(adesc)
    if not md:
      raise NotInstalledError('Not installed: %s' % (str(adesc)), adesc)
    return md
