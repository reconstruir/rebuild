#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from bes.fs import file_checksum, file_checksum_list
from .db_error import *
from .util import util

class files_db(object):

  SCHEMA_FILES = '''
CREATE TABLE {table_name} (
  filename  TEXT PRIMARY KEY NOT NULL, 
  checksum  TEXT
);
'''
  
  def __init__(self, db):
    self._db = db

  @classmethod
  def table_name(clazz, name):
    return 'files_%s' % (name)

  def has_table(self, name):
    return self._db.has_table(self.table_name(name))
  
  def filenames_rows(self, name):
    table_name = self.table_name(name)
    if not self._db.has_table(table_name):
      raise NotInstalledError('not installed: %s' % (name), name)
    sql = 'select filename from {table_name} order by filename asc'.format(table_name = table_name)
    return self._db.select_all(sql)

  def filenames(self, name):
    return [ row[0] for row in self.filenames_rows(name) ]
  
  def file_checksums_rows(self, name):
    table_name = self.table_name(name)
    if not self._db.has_table(table_name):
      raise NotInstalledError('not installed: %s' % (name), name)
    sql = 'select filename, checksum from {table_name} order by filename asc'.format(table_name = table_name)
    return self._db.select_all(sql)
                        
  def file_checksums(self, name):
    rows = self.file_checksums_rows(name)
    result = file_checksum_list()
    for row in rows:
      result.append(file_checksum(*row))
    return result

  def add_table(self, name, files):
    'Does not commit'
    check.check_string(name)
    check.check_file_checksum_list(files)
    table_name = self.table_name(name)
    assert not self._db.has_table(table_name)
    schema = self.SCHEMA_FILES.format(table_name = table_name)
    self._db.execute(schema)
    for f in files:
      self._insert_file(table_name, f)

  def remove_table(self, name):
    'Does not commit'
    check.check_string(name)
    table_name = self.table_name(name)
    assert self._db.has_table(table_name)
    self._db.execute('drop table %s' % (table_name))
      
  def _insert_file(self, table_name, f):
    check.check_string(table_name)
    check.check_file_checksum(f)
    sql = 'insert into {table_name} (filename, checksum) values (?, ?)'.format(table_name = table_name)
    self._db.execute(sql, ( f.filename, f.checksum ))
