#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json, os.path as path

from bes.fs import file_checksum, file_util

from bes.common import check, json_util

from .source_finder_db_entry import source_finder_db_entry
from .source_tool import source_tool

class source_finder_db_file(object):

  DB_FILENAME = 'sources_db.json'
  
  def __init__(self):
    self._db = {}

  def __getitem__(self, key):
    return self._db[key]

  def __setitem__(self, key, item):
    self._db[key] = item
    
  def __set_item____init__(self):
    self._db = {}

  def save_to_file(self, filename):
    json_util.save_file(filename, self._db, indent = 2)

  @classmethod
  def from_json(clazz, s):
    return clazz.from_json_object(json.loads(s))
    
  @classmethod
  def from_json_object(clazz, o):
    result = {}
    check.check_dict(o)
    for filename, list_item in o.items():
      check.check_list(list_item)
      result[filename] = source_finder_db_entry.from_list(list_item)
    return result
  
  @classmethod
  def from_file(clazz, filename):
    return clazz.from_json(file_util.read(filename))
    
  def to_json(self):
    return json.dumps(self._db, indent = 2)
  
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
      db[f] = source_finder_db_entry(f, mtime, checksum)
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
