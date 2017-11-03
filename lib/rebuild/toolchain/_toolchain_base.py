#!/usr/bin/env python
#-*- coding:utf-8 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common import string_util

class _toolchain_base(with_metaclass(ABCMeta, object)):

  def __init__(self, build_target):
    self.build_target = build_target

  @abstractmethod
  def is_valid(self):
    pass

  @abstractmethod
  def compiler_environment(self):
    pass

  @abstractmethod
  def compiler_flags(self):
    pass

  @abstractmethod
  def sysroot(self):
    pass
  
  @abstractmethod
  def sysroot_flags(self):
    pass
  
  def compiler_flags_flat(self):
    compiler_flags = self.compiler_flags()
    result = {}
    for key, flags in compiler_flags.items():
      result[key] = ' '.join(flags)
    return result
