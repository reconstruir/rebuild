#!/usr/bin/env python
#-*- coding:utf-8 -*-

from ._toolchain_base import _toolchain_base

from rebuild import build_type
from rebuild.toolchain.darwin.xcrun import xcrun
from rebuild.toolchain.darwin import darwin_sdk
import os.path as path

class _toolchain_darwin(_toolchain_base):

  def __init__(self, build_target):
    super(_toolchain_darwin, self).__init__(build_target)
    self.sdk = darwin_sdk.SYSTEM_TO_SDK[self.build_target.system]
    
  def compiler_environment(self):
    ar_replacement = path.abspath(path.normpath(path.join(path.dirname(__file__), '../../../bin/rebuild_ar.py')))
    env = {
      'CC': xcrun.find_tool(self.sdk, 'clang'),
      'CXX': xcrun.find_tool(self.sdk, 'clang++'),
      'RANLIB': xcrun.find_tool(self.sdk, 'ranlib'),
      'STRIP': xcrun.find_tool(self.sdk, 'strip'),
      'AR': ar_replacement,
      'AR_REAL': xcrun.find_tool(self.sdk, 'ar'),
      'AR_FLAGS': 'r',
      'ARFLAGS': 'r',
      'LIPO': xcrun.find_tool(self.sdk, 'lipo'),
      'APPLE_LIBTOOL': xcrun.find_tool(self.sdk, 'libtool'),
      'NM': xcrun.find_tool(self.sdk, 'nm'),
      'LD': xcrun.find_tool(self.sdk, 'clang'),
    }
    return env

  def compiler_flags(self):
    'Return the compiler flags for the given darwin.'

    arch_flags = self._make_arch_flags(self.build_target.archs)

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
      'REBUILD_COMPILE_ARCHS': self.build_target.archs,
    }
    
    return env

  @classmethod
  def _make_arch_flags(clazz, archs):
    'Return compiler flags for the given list of archs.'
    arch_flags = []
    for arch in archs:
      arch_flags += [ '-arch', arch ]
    return arch_flags

  def sysroot(self, build_target):
    return path.join(xcrun.sdk_path(self.sdk), 'usr')
