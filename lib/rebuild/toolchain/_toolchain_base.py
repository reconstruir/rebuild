#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class _toolchain_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def compiler_environment(self, build_target):
    pass

  @abstractmethod
  def compiler_flags(clazz, build_target):
    pass
