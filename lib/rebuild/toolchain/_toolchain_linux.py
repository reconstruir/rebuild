#!/usr/bin/env python
#-*- coding:utf-8 -*-

from ._toolchain_base import _toolchain_base
from rebuild.base import build_arch, build_level
import os.path as path

class _toolchain_linux(_toolchain_base):

  def __init__(self, build_target):
    super(_toolchain_linux, self).__init__(build_target)

  def is_valid(self):
    return True
    
  def compiler_environment(self):
    env = {
      'CPP': 'cpp',
      'CC': 'gcc',
      'CXX': 'g++',
      'CC_GCC': 'gcc',
      'CC_GPP': 'g++',
      'RANLIB': 'ranlib',
      'STRIP': 'strip',
      'AR': 'ar',
      'AR_REPLACEMENT': self.ar_replacement_program_exe(),
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

    arch_flags = self._make_arch_flags(self.build_target.arch)
    pic_flags = [ '-fPIC' ]

    if self.build_target.level == build_level.RELEASE:
      opt_flags = [ '-O2' ]
    else:
      opt_flags = [ '-g' ]

    cflags = arch_flags + opt_flags + pic_flags
    
    ldflags = []
      
    env = {
      'CPPFLAGS': [],
      'CFLAGS': cflags,
      'LDFLAGS': ldflags,
      'CXXFLAGS': cflags,
      'REBUILD_COMPILE_OPT_FLAGS': opt_flags,
      'REBUILD_COMPILE_ARCH_FLAGS': arch_flags,
      'REBUILD_COMPILE_ARCHS': [],
    }
    return env

  @classmethod
  def _make_arch_flags(clazz, archs):
    'Return compiler flags for the given list of archs.'
    assert len(archs) == 1
    if archs[0] == build_arch.I386:
      return [ '-m32' ]
    elif archs[0] == build_arch.X86_64:
      return [ '-m64' ]
    elif archs[0] == build_arch.ARMV7:
      return []
    else:
      raise ValueError('Invalid archs: %s' % (archs))

  def sysroot(self):
    return '/'

  def sysroot_cflags(self):
    'Return the sysroot CFLAGS.'
    return []

  def sysroot_cxxflags(self):
    'Return the sysroot CXXFLAGS.'
    return []

  def autoconf_flags(self):
    return [
#      '--host=%s' % (self._triplet),
#      '--sysroot %s' % (self._sysroot_platform_dir),
    ]
