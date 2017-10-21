#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class _strip_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def strip(self, build_target, binary):
    pass
