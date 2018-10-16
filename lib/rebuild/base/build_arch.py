#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, platform
from .build_system import build_system
from bes.common import check, string_util

class build_arch(object):

  ARMV7 = 'armv7'
  ARM64 = 'arm64'
  I386 = 'i386'
  X86_64 = 'x86_64'

#  MIPS = 'mips'
#  MIPS64 = 'mips64'

  VALID_ARCHS = {
    build_system.ANDROID: [ ARMV7 ],
    build_system.MACOS: [ I386, X86_64 ],
    build_system.IOS: [ ARM64, ARMV7 ],
    build_system.IOS_SIM: [ I386, X86_64 ],
    build_system.LINUX: [ I386, X86_64, ARMV7 ],
  }

  KNOWN_ARCHS = [ ARMV7, ARM64, I386, X86_64 ]

  HOST_ARCH = platform.machine()
  # deal with armv7l, armv7b
  if HOST_ARCH.startswith('armv7'):
    HOST_ARCH = ARMV7
  if not HOST_ARCH in KNOWN_ARCHS:
    raise ValueError('Unknown host arch: %s' % (HOST_ARCH))

  DEFAULT_ARCHS = {
    build_system.ANDROID: [ ARMV7 ],
    #build_system.MACOS: [ I386, X86_64 ],
    build_system.MACOS: [ X86_64 ],
    build_system.IOS: [ ARM64, ARMV7 ],
    build_system.IOS_SIM: [ I386, X86_64 ],
    build_system.LINUX: [ HOST_ARCH ],
  }

  DEFAULT_HOST_ARCHS = DEFAULT_ARCHS[build_system.HOST]

  @classmethod
  def determine_arch(clazz, system, arch, distro):
    result = []
    if system == build_system.LINUX:
      return clazz._determine_arch_linux(arch, distro)
    elif system == build_system.MACOS:
      return clazz._determine_arch_macos(arch)
    elif system == build_system.IOS:
      return clazz._determine_arch_ios(arch)
    elif system == build_system.ANDROID:
      return clazz._determine_arch_android(arch)
    else:
      raise ValueError('Invalid system: %s' % (str(system)))

  @classmethod
  def _determine_arch_linux(clazz, arch, distro):
    if check.is_string(arch):
      if arch in clazz.VALID_ARCHS[build_system.LINUX]:
        return ( arch, )
    elif check.check(arch, ( tuple, list )):
      if len(arch) == 1 and arch[0] in clazz.VALID_ARCHS[build_system.LINUX]:
        return ( arch[0], )
    raise ValueError('Invalid linux arch: %s' % (str(arch)))

  @classmethod
  def _determine_arch_macos(clazz, arch):
    if check.is_string(arch):
      if arch in clazz.VALID_ARCHS[build_system.MACOS]:
        return ( arch )
    elif check.check(arch, ( tuple, list )):
      if not False in [ a in clazz.VALID_ARCHS[build_system.LINUX] for a in arch ]:
        return tuple(arch)
    raise ValueError('Invalid linux arch: %s' % (str(arch)))

  @classmethod
  def _determine_arch_ios(clazz, arch):
    if check.is_string(arch):
      if arch in clazz.VALID_ARCHS[build_system.IOS]:
        return ( arch )
    elif check.check(arch, ( tuple, list )):
      if not False in [ a in clazz.VALID_ARCHS[build_system.IOS] for a in arch ]:
        return tuple(arch)
    raise ValueError('Invalid ios arch: %s' % (str(arch)))
  
  @classmethod
  def _determine_arch_android(clazz, arch):
    if check.is_string(arch):
      if arch in clazz.VALID_ARCHS[build_system.ANDROID]:
        return ( arch )
    elif check.check(arch, ( tuple, list )):
      if not False in [ a in clazz.VALID_ARCHS[build_system.ANDROID] for a in arch ]:
        return tuple(arch)
    raise ValueError('Invalid android arch: %s' % (str(arch)))
  
  @classmethod
  def arch_is_valid(clazz, arch, system):
    if system not in build_system.SYSTEMS:
      raise ValueError('Unknown system: %d' % (system))
    return arch in clazz.VALID_ARCHS[system]

  @classmethod
  def arch_to_string(clazz, arch, delimiter = ','):
    if isinstance(arch, ( tuple, list ) ):
      return delimiter.join(sorted(arch))
    return arch

  @classmethod
  def parse_arch(clazz, system, s):
    archs = s.split(',')
    for arch in archs:
      if not clazz.arch_is_valid(arch, system):
        raise ValueError('Invalid arch \"%s\" for system \"%s\"' % (arch, system))
    return tuple(sorted(archs))

  @classmethod
  def arch_is_known(clazz, arch):
    return arch in clazz.KNOWN_ARCHS
