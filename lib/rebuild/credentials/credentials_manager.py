#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check

class credentials_manager(object):

  def __init__(self):
    self._sources = []

  def add_source(self, source):
    check.check_credentials_source(source)
    self._sources.append(source)

  def is_valid(self):
    for source in self._sources:
      if source.is_valid():
        return True
    return False
    
  def credentials(self):
    for source in self._sources:
      if source.is_valid():
        return source.credentials()
      
check.register_class(credentials_manager, include_seq = False)
