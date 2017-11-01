#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass

class _toolchain_base(with_metaclass(ABCMeta, object)):

  def __init__(self, build_target):
    self.build_target = build_target
    
  @abstractmethod
  def compiler_environment(self):
    pass

  @abstractmethod
  def compiler_flags(clazz):
    pass

  @abstractmethod
  def sysroot(clazz):
    pass
  
