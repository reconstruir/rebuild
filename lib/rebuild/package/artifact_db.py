#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_check
from bes.common import check, string_util
from bes.sqlite import sqlite
from rebuild.base import package_descriptor_list

from .package_metadata import package_metadata
from .util import util

class ArtifactAlreadyInstalledError(Exception):
  def __init__(self, message, adesc):
    super(ArtifactAlreadyInstalledError, self).__init__()
    self.message = message
    self.adesc = adesc

  def __str__(self):
    return self.message

class ArtifactNotInstalledError(Exception):
  def __init__(self, message, adesc):
    super(ArtifactNotInstalledError, self).__init__()
    self.message = message
    self.adesc = adesc

  def __str__(self):
    return self.message
  
class artifact_db(object):

  SCHEMA_ARTIFACTS = '''
CREATE TABLE artifacts(
  id              INTEGER PRIMARY KEY NOT NULL,
  name            TEXT NOT NULL, 
  filename        TEXT NOT NULL, 
  checksum        TEXT NOT NULL, 
  version         TEXT NOT NULL, 
  revision        INTEGER NOT NULL, 
  epoch           INTEGER NOT NULL, 
  system          TEXT NOT NULL, 
  level           TEXT NOT NULL, 
  archs           TEXT NOT NULL, 
  distro          TEXT, 
  requirements    TEXT,
  properties      TEXT
);
'''

  SCHEMA_FILES = '''
CREATE TABLE {files_table_name}(
  filename  TEXT PRIMARY KEY NOT NULL, 
  checksum  TEXT
);
'''

  def __init__(self, filename):
    self._filename = path.abspath(filename)
    self._db = sqlite(self._filename)
    self._db.ensure_table('artifacts', self.SCHEMA_ARTIFACTS)
    self._files = {}
    
  @property
  def filename(self):
    return self._filename

###  def names(self):
###    rows = self._db.select('''SELECT name FROM artifacts ORDER by name ASC''')
###    return [ row[0] for row in rows ]
  
###  def package_files(self, name):
###    if not name in self._files:
###      p = self.find_package(name)
###      if not p:
###        raise PackageNotInstalledError('not installed: %s' % (name), name)
###      self._files[name] = set(p.files.filenames())
###    return self._files[name]

###  @classmethod
###  def _files_table_name(clazz, name):
###    return 'files_%s' % (name)
###
###  def _files_table_rows(self, name):
###    table_name = self._files_table_name(name)
###    return self._db.select_namedtuples('''SELECT * FROM %s ORDER by filename ASC''' % (table_name))
                        
  def _list_all_entries(self):
    rows = self._db.select_namedtuples('''SELECT * FROM artifacts ORDER by name ASC''')
    return [ package_metadata.from_sql_row(row, self._files_table_rows(row.name)) for row in rows ]
  
  def list_all(self, include_version = False):
    if not include_version:
      rows = self._db.select_namedtuples('''SELECT name FROM artifacts''')
      return [ row.name for row in rows ]
    rows = self._db.select_namedtuples('''SELECT name, version, revision, epoch FROM artifacts''')
    result = []
    for row in rows:
      entry = package_metadata.from_sql_row(row, [])
      result.append(entry.descriptor.full_name)
    return sorted(result)

  def has_artifact(self, adesc):
    sql = 'select count(name) from artifacts where {}'.format(adesc.WHERE_EXPRESSION)
    print('sql: %s' % (sql))
    t = adesc.to_sql_tuple()
    print('archs: %s - %s' % (t[6], type(t[6])))
    print('tup: %s' % (str(t)))
    row = self._db.select_one(sql, adesc.to_sql_tuple())
    print('row: %s' % (str(row)))
    return row[0] > 0

  def add_artifact(self, md):
    check.check_package_metadata(md)
    adesc = md.artifact_descriptor
    if self.has_artifact(adesc):
      raise ArtifactAlreadyInstalledError('Already installed: %s' % (str(adesc)), adesc)
    d = md.to_sql_dict()
    keys = ', '.join(d.keys())
    values = ', '.join(d.values())
    self._db.execute('insert into artifacts(%s) values(%s)' % (keys, values))

#    files_table_name = 'files_%s' % (md.name)
#    schema = self.SCHEMA_FILES.format(files_table_name = files_table_name)
#    self._db.execute(schema)
#    for f in md.files:
#      self._insert_file(files_table_name, f)

    self._db.commit()

###  def _insert_file(self, table_name, f):
###    check.check_string(table_name)
###    check.check_file_checksum(f)
###    if f.checksum is None:
###      checksum = 'null'
###    else:
###      checksum = string_util.quote(f.checksum, quote_char = "'")
###    sql = """INSERT INTO %s (filename, checksum) values ('%s', %s)""" % (table_name, f.filename, checksum)
###    self._db.execute(sql)
    
  def remove_artifact(self, adesc):
    check.check_artifact_descriptor(adesc)
    if not self.has_package(adesc):
      raise ArtifactNotInstalledError('Not installed: %s' % (adesc), adesc)
    sql = 'delete from artifacts {expression}'.format(adesc.WHERE_EXPRESSION)
    self._db.execute(sql, adesc)
    self._db.execute('DROP TABLE %s' % (self._files_table_name(name)))
    self._db.commit()

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
