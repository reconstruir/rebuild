#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path

from collections import namedtuple
from bes.common import object_util
from bes.fs import file_util
from rebuild import package_descriptor, version

from .DatabaseEntry import DatabaseEntry

class package_database(object):

  def __init__(self, filename):
    self.filename = filename
    if path.exists(self.filename):
      if not path.isfile(self.filename):
        raise RuntimeError('database exits and is not a file: %s' % (self.filename))
      self.db = self.__db_load(filename)
    else:
      self.db = {}
      
  def list_all(self, include_version = False):
    result = []
    for entry in self.db.values():
      if include_version:
        result.append(entry.info.full_name)
      else:
        result.append(entry.info.name)
    return sorted(result)

  def has_package(self, name):
    return name in self.db

  def add_package(self, package_info, files):
    if self.has_package(package_info.name):
      raise RuntimeError('Package database already has \"%s\"' % (package_info.name))
    self.db[package_info.name] = DatabaseEntry(package_info, files)
    self.__save()

  def remove_package(self, name):
    if not self.has_package(name):
      raise RuntimeError('Package database does not have \"%s\"' % (name))
    del self.db[name]
    self.__save()

  def find_package(self, name):
    package = self.db.get(name, None)
    if not package:
      return None
    assert isinstance(package, DatabaseEntry)
    return package

  def packages_with_files(self, files):
    files = object_util.listify(files)
    result = []
    for name, entry in self.db.items():
      if entry.has_any_files(files):
        result.append(name)
    return result

  def __save(self):
    self.__db_save(self.db, self.filename)

  @classmethod
  def __db_load(clazz, filename):
    content = file_util.read(filename)
    db = json.loads(content)
    for key, value in db.items():
      assert isinstance(value, dict)
      db[key] = DatabaseEntry.parse_dict(value)
    return db

  @classmethod
  def __db_save(clazz, db, filename):
    def default(o):
      if isinstance(o, DatabaseEntry):
        return o.to_dict()
      return o.__dict__
    s = json.dumps(db, indent = 2, default = default, sort_keys = True)
    file_util.backup(filename)
    file_util.save(filename, s)

  def list_all_descriptors(self):
    return sorted([entry.info for entry in self.db.values() ])