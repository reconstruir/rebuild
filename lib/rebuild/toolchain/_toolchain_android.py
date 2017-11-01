#!/usr/bin/env python
#-*- coding:utf-8 -*-

from ._toolchain_base import _toolchain_base

from rebuild import build_type
from rebuild.darwin.Xcrun import Xcrun
from rebuild.darwin.Sdk import Sdk
import os.path as path

class _toolchain_android(_toolchain_base):

  def __init__(self, build_target):
    super(_toolchain_android, self).__init__(build_target)
    self.sdk = Sdk.SYSTEM_TO_SDK[self.build_target.system]
    
  @classmethod
  def compiler_environment(clazz):
    ar_replacement = path.abspath(path.normpath(path.join(path.dirname(__file__), '../../../bin/rebuild_ar.py')))
    env = {
      'CC': Xcrun.find_tool(self.sdk, 'clang'),
      'CXX': Xcrun.find_tool(self.sdk, 'clang++'),
      'RANLIB': Xcrun.find_tool(self.sdk, 'ranlib'),
      'STRIP': Xcrun.find_tool(self.sdk, 'strip'),
      'AR': ar_replacement,
      'AR_REAL': Xcrun.find_tool(self.sdk, 'ar'),
      'AR_FLAGS': 'r',
      'ARFLAGS': 'r',
      'LIPO': Xcrun.find_tool(self.sdk, 'lipo'),
      'APPLE_LIBTOOL': Xcrun.find_tool(self.sdk, 'libtool'),
      'NM': Xcrun.find_tool(self.sdk, 'nm'),
      'LD': Xcrun.find_tool(self.sdk, 'clang'),
    }
    return env

  @classmethod
  def compiler_flags(clazz):
    'Return the compiler flags for the given darwin.'

    arch_flags = clazz._make_arch_flags(self.build_target.archs)

    if self.build_target.build_type == build_type.RELEASE:
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
  def _make_arch_flags(clazz, archs):
    'Return compiler flags for the given list of archs.'
    arch_flags = []
    for arch in archs:
      arch_flags += [ '-arch', arch ]
    return arch_flags

  @abstractmethod
  def sysroot(clazz, build_target):
    self.sdk_path = Xcrun.self.sdk_path(self.sdk)
    return path.join(self.sdk_path, 'usr')
