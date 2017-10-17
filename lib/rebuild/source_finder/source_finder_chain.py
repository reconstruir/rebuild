#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check_type
from rebuild import TarballUtil

from .source_finder import source_finder 

class source_finder_chain(object):

  def __init__(self):
    self._finders = []

  def add_finder(self, finder):
    check_type.check(finder, source_finder, 'finder')
    assert finder not in self._finders
    self._finders.append(finder)
    
  def find_source(self, name, version, build_target):
    for finder in self._finders:
      result = finder.find_source(name, version, build_target)
      if result:
        return result
    return None
