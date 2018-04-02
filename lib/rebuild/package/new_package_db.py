#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.sqlite import sqlite
from rebuild.base import package_descriptor_list

from .new_package_db_entry import new_package_db_entry

class new_package_db(object):

  SCHEMA_PACKAGES = '''
CREATE TABLE packages(
  name            TEXT PRIMARY KEY NOT NULL, 
  version         TEXT NOT NULL, 
  revision        INTEGER NOT NULL, 
  epoch           INTEGER NOT NULL, 
  requirements    TEXT,
  properties      TEXT,
  files           TEXT
);
'''
  
  def __init__(self, filename):
    self._filename = path.abspath(filename)
    self._db = sqlite(self._filename)
    self._db.ensure_table('packages', self.SCHEMA_PACKAGES)
    
  @property
  def filename(self):
    return self._filename
  
  def list_all(self, include_version = False):
    rows = self._db.select_namedtuples('''SELECT * FROM packages''')
    result = []
    for row in rows:
      entry = new_package_db_entry.from_sql_row(row)
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
    check.check_new_package_db_entry(entry)
    d = entry.to_sql_dict()
    keys = ', '.join(d.keys())
    values = ', '.join(d.values())
    sql = 'INSERT INTO packages(%s) values(%s)' % (keys, values)
    self._db.execute(sql)
    self._db.commit()
    
  def remove_package(self, name):
    t = ( name, )
    self._db.execute('DELETE FROM packages WHERE name=?', t)
    self._db.commit()

  def find_package(self, name):
    t = ( name, )
    rows = self._db.select_namedtuples('''SELECT * FROM packages where name=?''', t)
    if rows:
      return new_package_db_entry.from_sql_row(rows[0])
    return None

  def packages_with_files(self, files):
    assert False and 'FXIME'
    files = object_util.listify(files)
    result = []
    for name, entry in self.db.items():
      if entry.has_any_files(files):
        result.append(name)
    return result

  def list_all_descriptors(self):
    self._db.execute('SELECT * FROM packages')
    rows = self._db.select_namedtuples('''SELECT * FROM packages''')
    rows = [ new_package_db_entry.from_sql_row(row) for row in rows ]
    result = package_descriptor_list([ row.descriptor for row in rows ])
    result.sort()
    return result
