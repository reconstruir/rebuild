#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from rebuild import build_type

class SystemCompilersLinux(object):
  
  @classmethod
  def compilers_environment(clazz, build_target):
    'Return the compiler environment for linux'

    ar_replacement = path.abspath(path.normpath(path.join(path.dirname(__file__), '../../../bin/rebuild_ar.py')))

    env = {
      'CC': 'gcc',
      'CXX': 'g++',
      'CC_GCC': 'gcc',
      'CC_GPP': 'g++',
      'RANLIB': 'ranlib',
      'STRIP': 'strip',
      'AR': 'ar',
      'AR_REPLACEMENT': ar_replacement,
      'AR_REAL': 'ar',
      'AR_FLAGS': 'r',
      'ARFLAGS': 'r',
      'AR_REAL_FLAGS': 'r',
      'NM': 'nm',
      'LD': 'ld',
    }
    
    return env

  @classmethod
  def compiler_flags(clazz, build_target):
    'Return the compiler flags for the given darwin.'

    arch_flags = []
    pic_flags = [ '-fPIC' ]

    if build_target.build_type == build_type.RELEASE:
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
