#!/usr/bin/env python
#-*- coding:utf-8 -*-

from ._toolchain_base import _toolchain_base

from rebuild.base import build_level
from rebuild.toolchain.darwin.xcrun import xcrun
from rebuild.toolchain.darwin import darwin_sdk
import os.path as path

class _toolchain_darwin(_toolchain_base):

  def __init__(self, build_target):
    super(_toolchain_darwin, self).__init__(build_target)
    self.sdk = darwin_sdk.SYSTEM_TO_SDK[self.build_target.system]
    #print(self.sdk)

  def is_valid(self):
    return path.isdir(self.sysroot())
    
  def compiler_environment(self):
    env = {
#      'CPP': xcrun.find_tool(self.sdk, 'cpp'),
      'CC': xcrun.find_tool(self.sdk, 'clang'),
      'CXX': xcrun.find_tool(self.sdk, 'clang++'),
      'RANLIB': xcrun.find_tool(self.sdk, 'ranlib'),
      'STRIP': xcrun.find_tool(self.sdk, 'strip'),
      'AR': xcrun.find_tool(self.sdk, 'ar'),
      'AR_REPLACEMENT': self.ar_replacement_program_exe(),
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

    sysroot_cflags = self.sysroot_cflags()
    sysroot_cxxflags = self.sysroot_cxxflags()
    arch_flags = self._make_arch_flags(self.build_target.arch)

    if self.build_target.level == build_level.RELEASE:
      opt_flags = [ '-O2' ]
    else:
      opt_flags = [ '-g' ]

    cflags = sysroot_cflags + arch_flags + opt_flags
    cxxflags = sysroot_cxxflags + arch_flags + opt_flags

    ldflags = []

    env = {
#      'CPPFLAGS': sysroot_cflags,
      'CFLAGS': cflags,
      'LDFLAGS': ldflags,
      'CXXFLAGS': cxxflags,
      'REBUILD_COMPILE_OPT_FLAGS': opt_flags,
      'REBUILD_COMPILE_ARCH_FLAGS': arch_flags,
      'REBUILD_COMPILE_ARCH': self.build_target.arch,
    }
    
    return env

  @classmethod
  def _make_arch_flags(clazz, archs):
    'Return compiler flags for the given list of archs.'
    arch_flags = []
    for arch in archs:
      arch_flags += [ '-arch', arch ]
    return arch_flags

  def sysroot(self):
    return xcrun.sdk_path(self.sdk)

  def sysroot_cflags(self):
    'Return the sysroot CFLAGS.'
    return [
      '-isystem %s' % (path.join(self.sysroot(), 'usr/include')),
    ]
  
  def sysroot_cxxflags(self):
    'Return the sysroot CXXFLAGS.'
    return [
      '-isystem %s' % (path.join(self.sysroot(), 'usr/include/c++')),
    ]
  
  def autoconf_flags(self):
    return [
#      '--host=%s' % (self._triplet),
#      '--sysroot %s' % (self._sysroot_platform_dir),
    ]
