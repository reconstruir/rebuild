#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_find
from .source_finder import source_finder

class local_source_finder(source_finder):

  def __init__(self, where):
    self.where = path.abspath(where)
    
  #@abstractmethod
  def find_source(self, name, version, system):
    return self._find_by_name_and_version(self.where, name, version, system)

  #@abstractmethod
  def find_tarball(self, filename):
    return self._find_by_filename(self.where, filename)
