#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import file_checksum, file_util

from bes.common import json_util

from .source_item import source_item
from .source_tool import source_tool

class source_finder_db(object):

  DB_FILENAME = 'sources_db.json'
  
  def __init__(self, root):
    self._root = root
    self.db_filename = path.join(self._root, self.DB_FILENAME)
    self._db = {}
    self._reload_db()

  def _reload_db(self):
    self._db = self._read_db_file(self.db_filename)
    current_sources = source_tool.find_sources(self._root)
    self._db = self._make_db(current_sources)
    self._save_db_file(self.db_filename)

  def _make_db(self, sources):
    db = {}
    for f in sources:
      p = path.join(self._root, f)
      mtime = file_util.mtime(p)
      checksum = self._read_checksum(f)
      db[f] = source_item(f, mtime, checksum)
    return db
      
  def _read_checksum(self, filename):
    p = path.join(self._root, filename)
    mtime = file_util.mtime(p)
    item = self._db.get(filename, None)
    if item:
      if mtime == item[1]:
        assert item[2]
        return item[2]
    return file_util.checksum('sha1', p)

  @classmethod
  def _read_db_file(clazz, filename):
    if not path.exists(filename):
      return {}
    return json_util.read_file(filename)

  def _save_db_file(self, filename):
    json_util.save_file(filename, self._db, indent = 2)

  def checksum(self, filename):
    return self._db[filename][2]

  def checksum_dict(self):
    d = {}
    for filename, item in self._db.items():
      d[filename] = item[2]
    return d

  def files(self):
    return sorted(self._db.keys())
