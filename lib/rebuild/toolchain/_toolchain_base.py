#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.python import package

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
  def sysroot_cflags(self):
    pass
  
  @abstractmethod
  def sysroot_cxxflags(self):
    pass
  
  @abstractmethod
  def autoconf_flags(self):
    pass
  
  def compiler_flags_flat(self):
    compiler_flags = self.compiler_flags()
    result = {}
    for key, flags in compiler_flags.items():
      result[key] = ' '.join(flags)
    return result

  def ar_replacement_program_exe(self):
#    x = package.get_data_program_exe('../../../bin/rebuild_ar.py', __file__, __name__)
    y = path.abspath(path.normpath(path.join(path.dirname(__file__), '../../../bin/rebuild_ar.py')))
#    print('GOOD: %s' % (y))
#    print(' BAD: %s' % (x))
    return y
