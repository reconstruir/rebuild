#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ._toolchain_base import _toolchain_base
from bes.system.host import host
from bes.build.build_arch import build_arch
from bes.build.build_blurb import build_blurb
from bes.build.build_level import build_level
from bes.build.build_system import build_system
import os, os.path as path

class _toolchain_android_standalone(_toolchain_base):

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
    super(_toolchain_android_standalone, self).__init__(build_target)
    self.ndk_root = os.environ.get('REBUILD_ANDROID_NDK_TOOLCHAIN_ARM_ROOT', None)
    if not self.ndk_root:
      build_blurb.blurb('rebuild', '*** ERROR *** Trying to use android NDK but REBUILD_ANDROID_NDK_TOOLCHAIN_ARM_ROOT is not set.')
      return
    self._triplet = 'arm-linux-androideabi'
#    self._api = '26'
#    self._api_dir = 'android-%s' % (self._api)
#    self._arch_dir = self._REBUILD_ARCH_TO_PLATFORM_ARCH[self.build_target.arch[0]]
#    self._platforms_dir = path.join(self.ndk_root, 'platforms')
    self._sysroot_dir = path.join(self.ndk_root, 'sysroot')
    self._bin_dir = path.join(self.ndk_root, 'bin')

  def is_valid(self):
    return self.ndk_root and path.isdir(self.ndk_root)
    
  def compiler_environment(self):
    env = {
      'CPP': self._bin_tool('cpp'),
      'CC': self._bin_tool('gcc'),
      'CXX': self._bin_tool('g++'),
      'RANLIB': self._bin_tool('ranlib'),
      'STRIP': self._bin_tool('strip'),
      'AR': self._bin_tool('ar'),
      #'AR': 'ar', #self.ar_replacement_program_exe(),
      'AR_REAL': self._bin_tool('ar'),
      'AR_FLAGS': 'r',
      'ARFLAGS': 'r',
      'LIPO': self._bin_tool('lipo'),
#      'APPLE_LIBTOOL': self._bin_tool('libtool'),
      'NM': self._bin_tool('nm'),
      'LD': self._bin_tool('ld'),
    }
    return env

  def compiler_flags(self):
    'Return the compiler flags for the given darwin.'
    sysroot_cflags = self.sysroot_cflags()
    arch_flags = []
    pic_flags = [ '-fPIC' ]

    if self.build_target.level == build_level.RELEASE:
      opt_flags = [ '-O2' ]
    else:
      opt_flags = [ '-g' ]

    cflags = sysroot_cflags + arch_flags + opt_flags + pic_flags
    
    ldflags = sysroot_cflags
      
    env = {
      'CPPFLAGS': [],
      'CFLAGS': cflags,
      'LDFLAGS': ldflags,
      'CXXFLAGS': cflags,
      'REBUILD_COMPILE_OPT_FLAGS': opt_flags,
      'REBUILD_COMPILE_ARCH_FLAGS': arch_flags,
      'REBUILD_COMPILE_ARCH': self.build_target.arch,
    }
    
    return env

  def _bin_tool(self, tool_name):
    tool_filename = '%s-%s' % (self._triplet, tool_name)
    return path.join(self._bin_dir, tool_filename)
    
  def sysroot(self):
    return self._sysroot_dir
  
  def sysroot_cflags(self):
    'Return the sysroot flags.'
    sysroot = self.sysroot()
    return [
      '-isystem %s' % (path.join(sysroot, 'usr/include')),
      '--sysroot %s' % (sysroot),
    ]

  def sysroot_cxxflags(self):
    'Return the sysroot flags.'
    sysroot = self.sysroot()
    return [
      '-isystem %s' % (path.join(self.ndk_root, 'include/c++')),
      '--sysroot %s' % (self._sysroot_platform_dir),
    ]

  def autoconf_flags(self):
    return [
      '--host=%s' % (self._triplet),
#      '--sysroot %s' % (self._sysroot_platform_dir),
    ]
