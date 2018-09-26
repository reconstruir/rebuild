#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, json, os.path as path

from bes.fs import file_checksum, file_util

from bes.common import check, json_util

from .source_finder_db_entry import source_finder_db_entry
from .source_tool import source_tool

class source_finder_db_file(object):

  DB_FILENAME = 'sources_db.json'
  
  def __init__(self, db = None):
    self._db = copy.deepcopy(db or {})

  def __getitem__(self, key):
    return self._db[key]

  def __setitem__(self, key, item):
    self._db[key] = item
    
  def __set_item____init__(self):
    self._db = {}

  def __eq__(self, o):
    if isinstance(o, self.__class__):
      return self._db == o._db
    elif isinstance(o, dict):
      return self._db == o
    raise TypeError('Invalid type for o: %s' % (type(o)))

  def save_to_file(self, filename):
    json_util.save_file(filename, self._db, indent = 2)

  @classmethod
  def from_json(clazz, s):
    return clazz.from_json_object(json.loads(s))
    
  @classmethod
  def from_json_object(clazz, o):
    db = {}
    check.check_dict(o)
    for filename, list_item in o.items():
      check.check_list(list_item)
      db[filename] = source_finder_db_entry.from_list(list_item)
    return clazz(db)
  
  @classmethod
  def from_file(clazz, filename):
    return clazz.from_json(file_util.read(filename))
    
  def to_json(self):
    return json.dumps(self._db, indent = 2)

  def files(self):
    return sorted(self._db.keys())
  
