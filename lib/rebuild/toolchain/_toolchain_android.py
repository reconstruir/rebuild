#!/usr/bin/env python
#-*- coding:utf-8 -*-

from ._toolchain_base import _toolchain_base
from bes.system import host
from rebuild import build_arch, build_type, System
import os, os.path as path

class _toolchain_android(_toolchain_base):

  def __init__(self, build_target):
    super(_toolchain_android, self).__init__(build_target)
    self.ndk_root = os.environ.get('REBUILD_ANDROID_NDK_ROOT', None)
    
  def is_valid(self):
    return self.ndk_root and path.isdir(self.ndk_root)
    
  def compiler_environment(self):
    ar_replacement = path.abspath(path.normpath(path.join(path.dirname(__file__), '../../../bin/rebuild_ar.py')))
    env = {
      'CC': self._find_tool('gcc'),
      'CXX': self._find_tool('g++'),
      'RANLIB': self._find_tool('ranlib'),
      'STRIP': self._find_tool('strip'),
      'AR': ar_replacement,
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
      'REBUILD_COMPILE_ARCHS': build_target.archs,
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

  @classmethod
  def _rebuild_arch_to_android_arch(clazz, build_target):
    return None
#    ARMV7 = 'armv7'
#  ARM64 = 'arm64'
#  I386 = 'i386'
#  X86_64 = 'x86_64'



    #ARM	arm-linux-androideabi
#ARM64	aarch64-linux-android
#MIPS	mipsel-linux-android
#MIPS64	mips64el-linux-android
#x86	i686-linux-android
#x86_64	x86_64-linux-android
  
  def sysroot_flags(self):
    'Return the sysroot flags.'
    return []
#    sysroot = self.sysroot()
#    return [
##      -isystem $NDK/sysroot/usr/include/$TRIPLE when compiling. The triple has the following mapping:
##      e -isysroot option, then the --sysroot option applies to libraries, but the -isysroot option applies to header file#s.
##--sysroot should still point to $NDK/platforms/android-$API/arch-$ARCH/.
#    ]
  
