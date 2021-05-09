#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, platform
from .build_system import build_system
from bes.common.check import check
from bes.common.string_util import string_util

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
    build_system.WINDOWS: [ X86_64 ],
  }

  KNOWN_ARCHS = [ ARMV7, ARM64, I386, X86_64 ]

  HOST_ARCH = platform.machine()
  # deal with armv7l, armv7b
  if HOST_ARCH.startswith('armv7'):
    HOST_ARCH = ARMV7
  elif HOST_ARCH.lower() in [ 'x86_64', 'amd64', 'x86' ]:
    HOST_ARCH = X86_64
  if not HOST_ARCH in KNOWN_ARCHS:
    raise ValueError('Unknown host arch: %s' % (HOST_ARCH))

  DEFAULT_ARCHS = {
    build_system.ANDROID: ( ARMV7, ),
    #build_system.MACOS: ( I386, X86_64 ),
    build_system.MACOS: ( X86_64, ),
    build_system.IOS: ( ARM64, ARMV7 ),
    build_system.IOS_SIM: ( I386, X86_64 ),
    build_system.LINUX: ( X86_64, ),
    build_system.WINDOWS: ( X86_64, ),
  }

  DEFAULT_HOST_ARCHS = DEFAULT_ARCHS[build_system.HOST]

  @classmethod
  def split(clazz, arch, delimiter = ','):
    'Split an arch string by delimiter.'
    check.check_string(arch)
    return tuple([ a.strip() for a in arch.split(delimiter) ])

  @classmethod
  def join(clazz, arch, delimiter = ','):
    'Join arch parts by delimiter.'
    check.check_string_seq(arch)
    arch = [ a.strip() for a in arch ]
    return delimiter.join(arch)
  
  @classmethod
  def normalize(clazz, arch):
   'Normalize arch into a tuple.'
   if check.is_string(arch):
     return tuple(sorted(clazz.split(arch)))
   elif check.is_string_seq(arch):
     result = []
     for a in arch:
       result.extend(list(clazz.split(a)))
     return tuple(sorted(result))
   else:
     raise TypeError('Invalid type for arch: %s - %s' % (str(arch), type(arch)))

  @classmethod
  def check_arch(clazz, arch, system, distro):
    'Check that arch is valid for system or raise an error.'
    if arch == 'any':
      return arch
    validated_arch = clazz.validate(arch, system, distro)
    if not validated_arch:
      raise ValueError('Invalid arch \"%s\" for system \"%s\"' % (arch, system))
    return validated_arch
    
  @classmethod
  def validate(clazz, arch, system, distro):
    'Return True normalized arch if it is valid for system otherwise None.'
    arch = clazz.normalize(arch)
    check.check_string_seq(arch)
    if system == 'any':
      return arch
    build_system.check_system(system)
    valid_archs = clazz.VALID_ARCHS[system]
    for next_arch in arch:
      if not next_arch in valid_archs:
        return None
    return arch
    
  @classmethod
  def default_arch(clazz, system, distro):
    'Return the default arch for system.'
    build_system.check_system(system)
    if system == build_system.LINUX:
      if distro == build_system.RASPBIAN:
        return ( clazz.ARMV7, )
    return clazz.DEFAULT_ARCHS[system]

  # FIXME666 nothing is done with distro other than default case
  @classmethod
  def determine_arch(clazz, arch, system, distro):
    if system == 'any':
      if not arch:
        return ( X86_64, )
      return clazz.normalize(arch)
    build_system.check_system(system)
    if not arch:
      return clazz.default_arch(system, distro)
    normalized_arch = clazz.normalize(arch)
    clazz.check_arch(arch, system, distro)
    return normalized_arch

  @classmethod
  def parse_arch(clazz, arch, system, distro):
    normalized_arch = clazz.normalize(arch)
    clazz.check_arch(arch, system, distro)
    return normalized_arch

  @classmethod
  def arch_is_known(clazz, arch):
    return arch in clazz.KNOWN_ARCHS
