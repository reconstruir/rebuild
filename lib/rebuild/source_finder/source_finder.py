#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class source_finder(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def find_source(self, name, version, build_target):
    pass
