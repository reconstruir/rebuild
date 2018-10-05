#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, json, os.path as path
from collections import namedtuple

from bes.fs import file_checksum, file_util
from bes.common import check, json_util

from .source_finder_db_entry import source_finder_db_entry
from .source_tool import source_tool

class source_finder_db_file(object):

  DB_FILENAME = 'sources_db.json'
  
  def __init__(self, db = None):
    self._db = copy.deepcopy(db or {})

  def __contains__(self, key):
    return key in self._db
    
  def __getitem__(self, key):
    return self._db[key]

  def __setitem__(self, key, item):
    check.check_source_finder_db_entry(item)
    self._db[key] = item

  def __iter__(self, o):
    return iter(self._db)
    
  def __eq__(self, o):
    if isinstance(o, self.__class__):
      return self._db == o._db
    elif isinstance(o, dict):
      return self._db == o
    raise TypeError('Invalid type for o: %s' % (type(o)))

  def get(self, key, default = None):
    return self._db.get(key, default)
  
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

  def checksum(self, filename):
    return self._db[filename].checksum

  def mtime(self, filename):
    return self._db[filename].mtime

  def files(self):
    return sorted(self._db.keys())
  
  def entries(self):
    return sorted(self._db.values())

  def dict_items(self):
    return sorted(self._db.items())

  def checksum_dict(self):
    d = {}
    for filename, item in self._db.items():
      d[filename] = item.checksum
    return d
  
  delta_result = namedtuple('delta_result', 'common, conflicts, in_a_only, in_b_only')
  def delta(self, other):
    check.check_source_finder_db_file(other)
    db_a = self
    db_b = other
    set_a = set(db_a.checksum_dict())
    set_b = set(db_b.checksum_dict())
    in_a_only = set_a - set_b
    in_b_only = set_b - set_a
    in_both = set_a | set_b

    #delta_result = namedtuple('delta_result', 'common, conflicts, in_a_only, in_b_only')
      
    print('in_a_only: %s' % (str(in_a_only)))
    print('in_b_only: %s' % (str(in_b_only)))
    print('in_both: %s' % (str(in_both)))
    
    return None
    
check.register_class(source_finder_db_file)
