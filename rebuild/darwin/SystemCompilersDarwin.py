#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common import Shell
from rebuild.build_type import build_type

from Xcrun import Xcrun
from Sdk import Sdk

class SystemCompilersDarwin(object):

  @classmethod
  def compilers_environment(clazz, build_target):
    'Return the compiler environment for the given darwin sdk.'
    sdk = Sdk.SYSTEM_TO_SDK[build_target.system]
    ar_replacement = path.abspath(path.normpath(path.join(path.dirname(__file__), '../../bin/rebuild_ar.py')))
    env = {
      'CC': Xcrun.find_tool(sdk, 'clang'),
      'CXX': Xcrun.find_tool(sdk, 'clang++'),
      'RANLIB': Xcrun.find_tool(sdk, 'ranlib'),
      'STRIP': Xcrun.find_tool(sdk, 'strip'),
      'AR': ar_replacement,
      'AR_REAL': Xcrun.find_tool(sdk, 'ar'),
      'AR_FLAGS': 'r',
      'ARFLAGS': 'r',
      'LIPO': Xcrun.find_tool(sdk, 'lipo'),
      'APPLE_LIBTOOL': Xcrun.find_tool(sdk, 'libtool'),
      'NM': Xcrun.find_tool(sdk, 'nm'),
      'LD': Xcrun.find_tool(sdk, 'clang'),
    }
    return env
    
  @classmethod
  def compiler_flags(clazz, build_target):
    'Return the compiler flags for the given darwin.'

    arch_flags = clazz.__make_arch_flags(build_target.archs)

    if build_target.build_type == build_type.RELEASE:
      opt_flags = [ '-O2' ]
    else:
      opt_flags = [ '-g' ]

    cflags = arch_flags + opt_flags

    ldflags = []
      
    env = {
      'CFLAGS': cflags,
      'LDFLAGS': ldflags,
      'CXXFLAGS': cflags,
      'REBUILD_COMPILE_OPT_FLAGS': opt_flags,
      'REBUILD_COMPILE_ARCH_FLAGS': arch_flags,
      'REBUILD_COMPILE_ARCHS': build_target.archs,
    }
    
    return env

  @classmethod
  def __make_arch_flags(clazz, archs):
    'Return compiler flags for the given list of archs.'
    arch_flags = []
    for arch in archs:
      arch_flags += [ '-arch', arch ]
    return arch_flags
