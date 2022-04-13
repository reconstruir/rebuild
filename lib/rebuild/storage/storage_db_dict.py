#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, json, os.path as path

from bes.fs.file_util import file_util
from bes.system.check import check
from bes.common.json_util import json_util

from .storage_db_base import storage_db_base
from .storage_db_entry import storage_db_entry

class storage_db_dict(storage_db_base):

  def __init__(self, db = None):
    db = db or {}
    check.check_dict(db)
    self._db = copy.deepcopy(db)

  def save_to_file(self, filename):
    json_util.save_file(filename, self._db, indent = 2)

  @classmethod
  def from_json(clazz, s):
    return clazz.from_json_dict(json.loads(s))
    
  @classmethod
  def from_json_dict(clazz, o):
    db = {}
    check.check_dict(o)
    for filename, list_item in o.items():
      check.check_list(list_item)
      db[filename] = storage_db_entry.from_list(list_item)
    return clazz(db)
  
  @classmethod
  def from_file(clazz, filename):
    return clazz.from_json(file_util.read(filename))
    
#check.register_class(storage_db_dict)
