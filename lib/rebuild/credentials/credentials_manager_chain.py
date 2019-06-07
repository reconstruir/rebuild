#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check

class credentials_manager_chain(object):

  def __init__(self):
    self._managers = []

  def add_manager(self, manager):
    check.check_credentials_manager(manager)
    self._managers.append(manager)

  def is_valid(self):
    for manager in self._managers:
      if manager.is_valid():
        return True
    return False
    
  def credentials(self):
    for manager in self._managers:
      if manager.is_valid():
        return manager.credentials()
      
check.register_class(credentials_manager_chain, include_seq = False)
