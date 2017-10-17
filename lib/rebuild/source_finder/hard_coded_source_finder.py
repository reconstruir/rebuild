#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .source_finder import source_finder

class hard_coded_source_finder(source_finder):

  def __init__(self, tarball, name, version, system):
    self._check_archive_valid(tarball)
    self._tarball = tarball
    
  def find_source(self, name, version, system):
    return self._tarball
