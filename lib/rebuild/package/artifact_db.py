#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from bes.fs import file_check
from bes.common import check, string_util
from bes.sqlite import sqlite
from .artifact_descriptor_list import artifact_descriptor_list

from .db_error import *
from .files_db import files_db
from .package_files import package_files
from .package_metadata import package_metadata
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
    keys, values = self._metadata_to_sql_keys_and_values(md)
    self._db.execute('insert into artifacts(%s) values(%s)' % (keys, values))
    files_table_name = md.artifact_descriptor.sql_table_name
    self._files_db.add_table(files_table_name, md.files.files)
    self._files_db.add_table(self._make_env_files_table_name(files_table_name), md.files.env_files)
    self._db.commit()

  def replace_artifact(self, md):
    check.check_package_metadata(md)
    adesc = md.artifact_descriptor
    if not self.has_artifact(adesc):
      raise NotInstalledError('Not installed: %s' % (str(adesc)), adesc)
    keys, values = self._metadata_to_sql_keys_and_values(md)
    self._db.execute('replace into artifacts(%s) values(%s)' % (keys, values))
    files_table_name = md.artifact_descriptor.sql_table_name
    self._files_db.remove_table(files_table_name)
    self._files_db.remove_table(self._make_env_files_table_name(files_table_name))
    self._files_db.add_table(files_table_name, md.files.files)
    self._files_db.add_table(self._make_env_files_table_name(files_table_name), md.files.env_files)
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
    sql = 'delete from artifacts where {}'.format(adesc.WHERE_EXPRESSION)
    self._db.execute(sql, adesc.to_sql_tuple())
    files_table_name = adesc.sql_table_name
    self._files_db.remove_table(files_table_name)
    self._files_db.remove_table(self._make_env_files_table_name(files_table_name))
    self._db.commit()

  def list_all(self):
    rows = self._db.select_namedtuples('''select * from artifacts order by name asc''')
    result = artifact_descriptor_list()
    for row in rows:
      result.append(artifact_descriptor(row.name,
                                        row.version,
                                        row.revision,
                                        row.epoch,
                                        row.system,
                                        row.level,
                                        json.loads(row.archs),
                                        row.distro))
    return result

###  def _list_all_entries(self):
###    rows = self._db.select_namedtuples('''SELECT * FROM artifacts ORDER by name ASC''')
###    return [ package_metadata.from_sql_row(row, self._files_table_rows(row.name)) for row in rows ]
  
###  def list_all(self, include_version = False):
###    if not include_version:
###      rows = self._db.select_namedtuples('''SELECT name FROM artifacts''')
###      return [ row.name for row in rows ]
###    rows = self._db.select_namedtuples('''SELECT name, version, revision, epoch FROM artifacts''')
###    result = []
###    for row in rows:
###      entry = package_metadata.from_sql_row(row, [])
###      result.append(entry.descriptor.full_name)
###    return sorted(result)

###  def find_package(self, name):
###    t = ( name, )
###    rows = self._db.select_namedtuples('''SELECT * FROM artifacts where name=?''', t)
###    if rows:
###      return package_metadata.from_sql_row(rows[0], self._files_table_rows(rows[0].name))
###    return None
###
###  def artifacts_with_files(self, files):
###    'Return a list of package names for any artifacts that contain files. '
###    files = set(files)
###    result = []
###    for name in self.names():
###      next_files = self.package_files(name)
###      common = files & next_files
###      if common:
###        result.append(name)
###    return result

  def available_artifacts(self, build_target):
    rows = self._db.select_namedtuples('''SELECT * FROM artifacts''')
    rows = [ package_metadata.from_sql_row(row, []) for row in rows ]
    return sorted(rows)
  
  def _load_artifact(self, adesc):
    sql = 'select * from artifacts where {}'.format(adesc.WHERE_EXPRESSION)
    rows = self._db.select_namedtuples(sql, adesc.to_sql_tuple())
    if not rows:
      return None
    assert(len(rows) == 1)
    row = rows[0]
    files_table_name = adesc.sql_table_name
    files = package_files(self._files_db.file_checksums(files_table_name),
                          self._files_db.file_checksums(self._make_env_files_table_name(files_table_name)),
                          row.files_checksum,
                          row.env_files_checksum)
    #filename, name, version, revision, epoch, system, level, archs, distro, requirements, properties, files
    return package_metadata(row.filename,
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
  
  def find_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    return self._load_artifact(adesc)

  def get_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    md = self._load_artifact(adesc)
    if not md:
      raise NotInstalledError('Not installed: %s' % (str(adesc)), adesc)
    return md
