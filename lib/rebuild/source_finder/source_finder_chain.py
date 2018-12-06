#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common import check

from .source_finder import source_finder 

class source_finder_chain(object):

  def __init__(self):
    self._finders = []

  def __str__(self):
    return ', '.join([ str(f) for f in self._finders ])

  def __len__(self):
    return len(self._finders)
  
  def add_finder(self, finder):
    check.check(finder, source_finder)
    assert finder not in self._finders
    self._finders.append(finder)
    
  def find_tarball(self, filename):
    for finder in self._finders:
      result = finder.find_tarball(filename)
      if result:
        return result
    return None

  def ensure_source(self, filename):
    assert path.isabs(filename)
    for finder in self._finders:
      if finder.ensure_source(filename):
        return True
    return False
  
  def search(self, name):
    result = []
    for finder in self._finders:
      result.extend(finder.search(name))
    return result
  
check.register_class(source_finder_chain, include_seq = False)
  
