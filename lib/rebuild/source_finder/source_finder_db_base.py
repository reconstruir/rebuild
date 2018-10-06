#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
import json
from bes.system.compat import with_metaclass
from bes.text import text_table
from bes.common import check
from collections import namedtuple

class source_finder_db_base(object):

  DB_FILENAME = 'sources_db.json'

  def __init__(self):
    self._db = None
  
  @abstractmethod
  def load(self):
    'Load the db from its source.'
    pass

  @abstractmethod
  def save(self):
    'Save the db from its source.'
    pass

  def __eq__(self, o):
    if isinstance(o, self.__class__):
      return self._db == o._db
    elif isinstance(o, dict):
      return self._db == o
    raise TypeError('Invalid type for o: %s' % (type(o)))
  
  def __contains__(self, filename):
    return filename in self._db
  
  def __getitem__(self, filename):
    return self._db[filename]

  def __setitem__(self, filename, entry):
    self._db[filename] = entry

  def __iter__(self, o):
    return iter(self._db)

  def get(self, filename, default = None):
    return self._db.get(filename, default)

  def mtime(self, filename):
    return self._db[filename].mtime

  def checksum(self, filename):
    return self._db[filename].checksum
  
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
  
  def delta(self, other):
    assert isinstance(other, self.__class__)
    return self._db.delta(other._db)

  delta_result = namedtuple('delta_result', 'common, conflicts, in_a_only, in_b_only')
  def delta(self, other):
    check.check_source_finder_db_base(other)
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
  
  def dump(self):
    tt = text_table(data = self.entries())
    print(str(tt))

  def to_json(self):
    return json.dumps(self._db, indent = 2)
      
  def find_by_checksum(self, checksum):
    for entry in self._db.itervalues():
      if entry.checksum == checksum:
        return entry
    return None
      
check.register_class(source_finder_db_base)
      
