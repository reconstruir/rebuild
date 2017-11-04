#!/usr/bin/env python
#-*- coding:utf-8 -*-

from ._toolchain_base import _toolchain_base
from bes.system import host
from rebuild import build_arch, build_type, System
import os, os.path as path

class _toolchain_android(_toolchain_base):

  _REBUILD_ARCH_TO_TRIPLET = {
    build_arch.ARMV7: 'arm-linux-androideabi',
    build_arch.ARM64: 'aarch64-linux-android',
    #build_arch.MIPS: 'mipsel-linux-android',
    #build_arch.MIPS64: 'mips64el-linux-android',
    build_arch.I386: 'i686-linux-android',
    build_arch.X86_64: 'x86_64-linux-android',
  }

  _REBUILD_ARCH_TO_PLATFORM_ARCH = {
    build_arch.ARMV7: 'arch-arm',
    build_arch.ARM64: 'arch-arm64',
    #build_arch.MIPS: 'arch-mips',
    #build_arch.MIPS64: 'arch-mips64',
    build_arch.I386: 'arch-x86',
    build_arch.X86_64: 'arch-x86_64',
  }
  
  def __init__(self, build_target):
    super(_toolchain_android, self).__init__(build_target)
    self.ndk_root = os.environ.get('REBUILD_ANDROID_NDK_ROOT', None)
    self._triplet = self._REBUILD_ARCH_TO_TRIPLET[self.build_target.archs[0]]
    self._api = '26'
    self._api_dir = 'android-%s' % (self._api)
    self._arch_dir = self._REBUILD_ARCH_TO_PLATFORM_ARCH[self.build_target.archs[0]]
    self._platforms_dir = path.join(self.ndk_root, 'platforms')
    
  def is_valid(self):
    return self.ndk_root and path.isdir(self.ndk_root)
    
  def compiler_environment(self):
    ar_replacement = path.abspath(path.normpath(path.join(path.dirname(__file__), '../../../bin/rebuild_ar.py')))
    env = {
      'CC': self._find_tool('gcc'),
      'CXX': self._find_tool('g++'),
      'RANLIB': self._find_tool('ranlib'),
      'STRIP': self._find_tool('strip'),
      'AR': 'ar', #ar_replacement,
      'AR_REAL': self._find_tool('ar'),
      'AR_FLAGS': 'r',
      'ARFLAGS': 'r',
      'LIPO': self._find_tool('lipo'),
#      'APPLE_LIBTOOL': self._find_tool('libtool'),
      'NM': self._find_tool('nm'),
      'LD': self._find_tool('ld'),
    }
    return env

  def compiler_flags(self):
    'Return the compiler flags for the given darwin.'
    sysroot_flags = self.sysroot_flags()
    arch_flags = []
    pic_flags = [ '-fPIC' ]

    if self.build_target.build_type == build_type.RELEASE:
      opt_flags = [ '-O2' ]
    else:
      opt_flags = [ '-g' ]

    cflags = sysroot_flags + arch_flags + opt_flags + pic_flags
    
    ldflags = sysroot_flags
      
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
  def _prebuilt_host(clazz):
    if host.SYSTEM == host.LINUX:
      return 'linux'
    elif host.SYSTEM == host.MACOS:
      return 'darwin'
    else:
      assert False
  
  def _find_tool(self, tool_exe):
    toolchain_name = 'arm-linux-androideabi'
    toolchain_version = '4.9'
    toolchain_dir = '%s-%s' % (toolchain_name, toolchain_version)
    prebuilt_host = self._prebuilt_host()
    prebuilt_arch = 'x86_64'
    prebuilt_dir = '%s-%s' % (prebuilt_host, prebuilt_arch)
    p = path.join(self.ndk_root, 'toolchains', toolchain_dir, 'prebuilt', prebuilt_dir, 'bin')
    tool_name = '%s-%s' % (toolchain_name, tool_exe)
    return path.join(p, tool_name)
    
  def sysroot(self):
    return path.join(self.ndk_root, 'sysroot')
  
  def sysroot_flags(self):
    'Return the sysroot flags.'
    sysroot = self.sysroot()
    return [
      '-isystem %s' % (path.join(sysroot, 'usr/include', self._triplet)),
      '--sysroot %s' % (path.join(self._platforms_dir, self._api_dir, self._arch_dir)),
    ]
