#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check

class imported_artifacts(object):

  def __init__(self):
    self._artifacts = set()
  
  def add(self, pdesc, bt):
    key = self._make_key(pdesc, bt)
    assert not key in self._artifacts
    self._artifacts.add(key)

  def has(self, pdesc, bt):
    key = self._make_key(pdesc, bt)
    return key in self._artifacts
    
  def _make_key(pdesc, bt):
    check.check_package_descriptor(pdesc)
    check.check_build_target(bt)
    return hash( ( pdesc, bt ) )
  
check.register_class(imported_artifacts, include_seq = False)
