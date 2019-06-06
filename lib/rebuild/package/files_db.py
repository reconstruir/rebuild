#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from bes.fs.file_checksum import file_checksum
from bes.fs.file_checksum import file_checksum_list
from bes.system import log

from .db_error import *
from .package_file import package_file
from .package_file_list import package_file_list

class files_db(object):

  SCHEMA_FILES = '''
CREATE TABLE {table_name} (
  filename           TEXT PRIMARY KEY NOT NULL, 
  checksum           TEXT,
  has_hardcoded_path BOOLEAN NOT NULL CHECK (has_hardcoded_path IN (0,1))
);
'''
  
  def __init__(self, db):
    log.add_logging(self, 'artifact_db')
    self._db = db

  @classmethod
  def table_name(clazz, name):
    return 'manifest_%s' % (name)

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
  
  def package_file_rows(self, name):
    table_name = self.table_name(name)
    if not self._db.has_table(table_name):
      raise NotInstalledError('not installed: %s' % (name), name)
    sql = 'select filename, checksum, has_hardcoded_path from {table_name} order by filename asc'.format(table_name = table_name)
    return self._db.select_all(sql)
                        
  def package_manifest(self, name):
    rows = self.package_file_rows(name)
    result = package_file_list()
    for row in rows:
      result.append(package_file(*row))
    return result

  def add_table(self, name, files):
    'Does not commit'
    check.check_string(name)
    check.check_package_file_list(files)
    table_name = self.table_name(name)
    self.log_d('files_db: add_table(name=%s) table_name=%s' % (name, table_name))
    if self._db.has_table(table_name):
      raise RuntimeError('%s: already has table: %s' % (self._db.filename, table_name))
    
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
    check.check_package_file(f)
    sql = 'insert into {table_name} (filename, checksum, has_hardcoded_path) values (?, ?, ?)'.format(table_name = table_name)
    self._db.execute(sql, ( f.filename, f.checksum, f.has_hardcoded_path ))
