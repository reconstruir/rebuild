#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
#from bes.fs import file_find
from .storage_base import storage_base
from .tarball_finder import tarball_finder

class storage_local(storage_base):

  def __init__(self, where):
    self.where = path.abspath(where)
    
  def __str__(self):
    return 'local:%s' % (self.where)
    
  #@abstractmethod
  def find_tarball(self, filename):
    return tarball_finder.find_by_filename(self.where, filename)

  #@abstractmethod
  def ensure_source(self, filename):
    assert path.isabs(filename)
    return path.isfile(filename)
  
  #@abstractmethod
  def search(self, name):
    pass
