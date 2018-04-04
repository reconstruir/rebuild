#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.sqlite import sqlite
from rebuild.base import package_descriptor_list

from .package_db_entry import package_db_entry

class PackageNotInstalledError(Exception):

  def __init__(self, message, name):
    super(PackageNotInstalledError, self).__init__(message)
    self.name = name
    
class package_db(object):

  SCHEMA_PACKAGES = '''
CREATE TABLE packages(
  name            TEXT PRIMARY KEY NOT NULL, 
  version         TEXT NOT NULL, 
  revision        INTEGER NOT NULL, 
  epoch           INTEGER NOT NULL, 
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
    self._db.ensure_table('packages', self.SCHEMA_PACKAGES)
    self._files = {}
    
  @property
  def filename(self):
    return self._filename

  def names(self):
    rows = self._db.select('''SELECT name FROM packages ORDER by name ASC''')
    return [ row[0] for row in rows ]
  
  def package_files(self, name):
    if not name in self._files:
      p = self.find_package(name)
      if not p:
        raise PackageNotInstalledError('not installed: %s' % (name), name)
      self._files[name] = set(p.files.filenames())
    return self._files[name]

  @classmethod
  def _files_table_name(clazz, name):
    return 'files_%s' % (name)

  def _files_table_rows(self, name):
    table_name = self._files_table_name(name)
    return self._db.select_namedtuples('''SELECT * FROM %s ORDER by filename ASC''' % (table_name))
                        
  def _list_all_entries(self):
    rows = self._db.select_namedtuples('''SELECT * FROM packages ORDER by name ASC''')
    return [ package_db_entry.from_sql_row(row, self._files_table_rows(row.name)) for row in rows ]
  
  def list_all(self, include_version = False):
    rows = self._db.select_namedtuples('''SELECT * FROM packages''')
    result = []
    for row in rows:
      entry = package_db_entry.from_sql_row(row, [])
      if include_version:
        result.append(entry.descriptor.full_name)
      else:
        result.append(entry.descriptor.name)
    return sorted(result)

  def has_package(self, name):
    t = ( name, )
    rows = self._db.select('''SELECT count(*) FROM packages WHERE name=?''', t)
    return rows[0][0] > 0

  def add_package(self, entry):
    check.check_package_db_entry(entry)
    d = entry.to_sql_dict()
    keys = ', '.join(d.keys())
    values = ', '.join(d.values())
    self._db.execute('INSERT INTO packages(%s) values(%s)' % (keys, values))
    files_table_name = 'files_%s' % (entry.name)
    schema = self.SCHEMA_FILES.format(files_table_name = files_table_name)
    self._db.execute(schema)
    for f in entry.files:
      self._insert_file(files_table_name, f)
    self._db.commit()

  def _insert_file(self, table_name, f):
    check.check_string(table_name)
    check.check_file_checksum(f)
    if f.checksum is None:
      checksum = 'null'
    else:
      checksum = string_util.quote(f.checksum, quote_char = "'")
    sql = """INSERT INTO %s (filename, checksum) values ('%s', %s)""" % (table_name, f.filename, checksum)
    self._db.execute(sql)
    
  def remove_package(self, name):
    if not self.has_package(name):
      raise PackageNotInstalledError('not installed: %s' % (name), name)
    t = ( name, )
    self._db.execute('DELETE FROM packages WHERE name=?', t)
    self._db.execute('DROP TABLE %s' % (self._files_table_name(name)))
    self._db.commit()

  def find_package(self, name):
    t = ( name, )
    rows = self._db.select_namedtuples('''SELECT * FROM packages where name=?''', t)
    if rows:
      return package_db_entry.from_sql_row(rows[0], self._files_table_rows(rows[0].name))
    return None

  def packages_with_files(self, files):
    'Return a list of package names for any packages that contain files. '
    files = set(files)
    result = []
    for name in self.names():
      next_files = self.package_files(name)
      common = files & next_files
      if common:
        result.append(name)
    return result

  def list_all_descriptors(self):
    self._db.execute('SELECT * FROM packages')
    rows = self._db.select_namedtuples('''SELECT * FROM packages''')
    rows = [ package_db_entry.from_sql_row(row) for row in rows ]
    result = package_descriptor_list([ row.descriptor for row in rows ])
    result.sort()
    return result
