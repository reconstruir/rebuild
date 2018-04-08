#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.sqlite import sqlite
from rebuild.base import package_descriptor_list
    
class files_db(object):

  SCHEMA_FILES = '''
CREATE TABLE {files_table_name}(
  filename  TEXT PRIMARY KEY NOT NULL, 
  checksum  TEXT
);
'''
  
  def __init__(self):
    self._files_db = None
    
  @property
  def files_db(self):
    if not self._files_db:
      raise RuntimeError('need to set files_db before using.')
    return self._files_db

  @files_db.setter
  def files_db(self, db):
    self._files_db = db

  def files_table_name(self, name):
    return 'files_%s' % (name)

  def files_table_rows(self, name):
    table_name = self.files_table_name(name)
    return self.files_db.select_namedtuples('''select * from %s order by filename asc''' % (table_name))
                        
  def add_files_table(self, name, files):
    'Does not commit'
    check.check_string(name)
    check.check_file_checksum_list(files)
    table_name = self.files_table_name(name)
    assert not self.files_db.has_table(table_name)
    schema = self.SCHEMA_FILES.format(files_table_name = table_name)
    self.files_db.execute(schema)
    for f in files:
      self._insert_file(table_name, f)

  def remove_files_table(self, name):
    'Does not commit'
    check.check_string(name)
    table_name = self.files_table_name(name)
    assert self.files_db.has_table(table_name)
    self.files_db.execute('drop table %s' % (table_name))
      
  def _insert_file(self, table_name, f):
    check.check_string(table_name)
    check.check_file_checksum(f)
    sql = 'insert into {table_name} (filename, checksum) values (?, ?)'.format(table_name = table_name)
    self.files_db.execute(sql, ( f.filename, f.checksum ))
