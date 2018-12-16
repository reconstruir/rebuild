#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path
from bes.common import check
from bes.sqlite import sqlite
from rebuild.base import build_version, package_descriptor, package_descriptor_list

from .db_error import *
from .files_db import files_db
from .package_db_entry import package_db_entry
from .package_files import package_files
from .sql_encoding import sql_encoding

class package_db(object):

  SCHEMA_PACKAGES = '''
create table packages(
  name                text primary key not null, 
  version             text not null, 
  revision            integer not null, 
  epoch               integer not null, 
  requirements        text,
  properties          text,
  files_checksum      text not null,
  env_files_checksum  text not null
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
                        
  def env_files(self, name):
    return self.files(self._make_env_files_table_name(name))
                        
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
    d =  {
      'name': sql_encoding.encode_string(entry.name),
      'version': sql_encoding.encode_string(entry.version),
      'revision': str(entry.revision),
      'epoch': str(entry.epoch),
      'requirements': sql_encoding.encode_requirements(entry.requirements),
      'properties': sql_encoding.encode_dict(entry.properties),
      'files_checksum': sql_encoding.encode_string(entry.files.files_checksum),
      'env_files_checksum': sql_encoding.encode_string(entry.files.env_files_checksum),
    }
    keys = ', '.join(d.keys())
    values = ', '.join(d.values())
    self._db.execute('insert into packages(%s) values(%s)' % (keys, values))
    self._files_db.add_table(entry.name, entry.files.files)
    self._files_db.add_table(self._make_env_files_table_name(entry.name), entry.files.env_files)
    self._db.commit()

  def remove_package(self, name):
    if not self.has_package(name):
      raise NotInstalledError('not installed: %s' % (name), name)
    t = ( name, )
    self._db.execute('delete from packages where name=?', t)
    self._files_db.remove_table(name)
    self._files_db.remove_table(self._make_env_files_table_name(name))
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
      self._packages[name] = self._load_package_db_entry(name)
    return self._packages[name]

  @classmethod
  def _make_env_files_table_name(clazz, name):
    return name + '_env'
  
  def _load_package_db_entry(self, name):
    rows = self._db.select_namedtuples('''select * from packages where name=?''', ( name, ))
    if not rows:
      raise NotInstalledError('not installed: %s' % (name), name)
    assert(len(rows) == 1)
    row = rows[0]
    files = package_files(self._files_db.package_files(name),
                          self._files_db.package_files(self._make_env_files_table_name(name)),
                          row.files_checksum,
                          row.env_files_checksum)
    return package_db_entry(row.name,
                            row.version,
                            row.revision,
                            row.epoch,
                            sql_encoding.decode_requirements(row.requirements),
                            json.loads(row.properties),
                            files)

  def dep_map(self):
    rows = self._db.select_namedtuples('''select name, requirements from packages''')
    if not rows:
      return {}
    dep_map = {}
    for row in rows:
      reqs = sql_encoding.decode_requirements(row.requirements)
      dep_map[row.name] = set(reqs.names())
    return dep_map
