#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from .source_finder import source_finder

class local_source_finder(source_finder):

  def __init__(self, where):
    self.where = path.abspath(where)
    
  def find_source(self, name, version, system):
    return self._find_tarball(self.where, name, version, system)
