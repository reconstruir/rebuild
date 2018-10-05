#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

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

  def __contains__(self, filename):
    return filename in self._db
  
  def __getitem__(self, filename):
    return self._db[filename]

  def __setitem__(self, filename, entry):
    self._db[filename] = entry

  def __iter__(self, o):
    return iter(self._db)
    
  def checksum(self, filename):
    return self._db.checksum(filename)

  def files(self):
    return self._db.files()

  def items(self):
    return self._db.items()

  def checksum_dict(self):
    return self._db.checksum_dict()
  
  def delta(self, other):
    assert isinstance(other, self.__class__)
    return self._db.delta(other._db)

  def dump(self):
    #check.check_source_finder_dbe(other)
    for filename in self.files():
      entry = db[filename]
      print('%s' % (str(entry)))
