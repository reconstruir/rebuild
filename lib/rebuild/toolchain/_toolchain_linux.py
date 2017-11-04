#!/usr/bin/env python
#-*- coding:utf-8 -*-

from ._toolchain_base import _toolchain_base
from rebuild import build_type
import os.path as path

class _toolchain_linux(_toolchain_base):

  def __init__(self, build_target):
    super(_toolchain_linux, self).__init__(build_target)

  def is_valid(self):
    return True
    
  def compiler_environment(self):
    ar_replacement = path.abspath(path.normpath(path.join(path.dirname(__file__), '../../../bin/rebuild_ar.py')))

    env = {
      'CC': 'gcc',
      'CXX': 'g++',
      'CC_GCC': 'gcc',
      'CC_GPP': 'g++',
      'RANLIB': 'ranlib',
      'STRIP': 'strip',
      'AR': 'ar',
      'AR_REPLACEMENT': 'ar', #ar_replacement,
      'AR_REAL': 'ar',
      'AR_FLAGS': 'r',
      'ARFLAGS': 'r',
      'AR_REAL_FLAGS': 'r',
      'NM': 'nm',
      'LD': 'ld',
    }
    
    return env

  def compiler_flags(self):
    'Return the compiler flags for the given darwin.'

    arch_flags = []
    pic_flags = [ '-fPIC' ]

    if self.build_target.build_type == build_type.RELEASE:
      opt_flags = [ '-O2' ]
    else:
      opt_flags = [ '-g' ]

    cflags = arch_flags + opt_flags + pic_flags
    
    ldflags = []
      
    env = {
      'CFLAGS': cflags,
      'LDFLAGS': ldflags,
      'CXXFLAGS': cflags,
      'REBUILD_COMPILE_OPT_FLAGS': opt_flags,
      'REBUILD_COMPILE_ARCH_FLAGS': arch_flags,
      'REBUILD_COMPILE_ARCHS': [],
    }
    return env

  def sysroot(self):
    return '/'

  def sysroot(self):
    return path.join(self.ndk_root, 'sysroot')
  
  def sysroot_flags(self):
    'Return the sysroot flags.'
    return [
    ]
