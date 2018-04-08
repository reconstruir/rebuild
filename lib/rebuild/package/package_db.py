#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from bes.common import check
from bes.sqlite import sqlite
from rebuild.base import build_version, package_descriptor, package_descriptor_list

from .package_db_entry import package_db_entry
from .files_db import files_db
from .util import util
from .db_error import *

class package_db(object):

  SCHEMA_PACKAGES = '''
create table packages(
  name            text primary key not null, 
  version         text not null, 
  revision        integer not null, 
  epoch           integer not null, 
  requirements    text,
  properties      text,
  checksum        text not null
);
'''
  
  SCHEMA_FILES = '''
create table {files_table_name}(
  filename  text primary key not null, 
  checksum  text
);
'''
  
  def __init__(self, filename):
    self._filename = path.abspath(filename)
    self._db = sqlite(self._filename)
    self._db.ensure_table('packages', self.SCHEMA_PACKAGES)
    self._files = {}
    self._files_db = files_db(self._db)
    self._packages = {}
    
  @property
  def filename(self):
    return self._filename

  def names(self):
    rows = self._db.select_all('''select name from packages order by name asc''')
    return [ row[0] for row in rows ]

  def descriptors(self):
    rows = self._db.select_namedtuples('''select name, version, revision, epoch from packages order by name asc''')
    result = package_descriptor_list()
    for row in rows:
      result.append(package_descriptor(row.name, build_version(row.version, row.revision, row.epoch)))
    return result
  
  def files(self, name):
    if not name in self._files:
      self._files[name] = set(self._files_db.filenames(name))
    return self._files[name]
                        
  def list_all(self, include_version = False):
    if not include_version:
      return self.names()
    return [ d.full_name for d in self.descriptors() ]

  def has_package(self, name):
    t = ( name, )
    row = self._db.select_one('''select count(*) from packages where name=?''', t)
    return row[0] > 0

  def add_package(self, entry):
    check.check_package_db_entry(entry)
    d = entry.to_sql_dict()
    keys = ', '.join(d.keys())
    values = ', '.join(d.values())
    self._db.execute('insert into packages(%s) values(%s)' % (keys, values))
    self._files_db.add_table(entry.name, entry.files)
    self._db.commit()

  def remove_package(self, name):
    if not self.has_package(name):
      raise NotInstalledError('not installed: %s' % (name), name)
    t = ( name, )
    self._db.execute('delete from packages where name=?', t)
    self._files_db.remove_table(name)
    self._db.commit()

  def packages_with_files(self, files):
    'Return a list of package names for any packages that contain any of the given files.'
    files = set(files)
    result = []
    for name in self.names():
      common = files & self.files(name)
      if common:
        result.append(name)
    return result

  def find_package(self, name):
    if not self.has_package(name):
      return None
    if name not in self._packages:
      self._packages[name] = self._load_package(name)
    return self._packages[name]

  def _load_package(self, name):
    rows = self._db.select_namedtuples('''select * from packages where name=?''', ( name, ))
    if not rows:
      raise NotInstalledError('not installed: %s' % (name), name)
    assert(len(rows) == 1)
    row = rows[0]
    return package_db_entry(row.name,
                            row.version,
                            row.revision,
                            row.epoch,
                            util.sql_decode_requirements(row.requirements),
                            json.loads(row.properties),
                            self._files_db.file_checksums(name),
                            row.checksum)
