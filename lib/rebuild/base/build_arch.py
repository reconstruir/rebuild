#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, platform
from .build_system import build_system
from bes.common import string_util

class build_arch(object):

  DEFAULT = 'default'

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
    build_system.LINUX: [ I386, X86_64 ],
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
  def determine_archs(clazz, system, tentative_archs):
    result = []
    if system == build_system.LINUX:
      return clazz._determine_archs_linux(system, tentative_archs)
    else:
      if not tentative_archs or tentative_archs == 'default':
        return clazz.DEFAULT_ARCHS[system]
      if string_util.is_string(tentative_archs):
        return clazz.parse_archs(system, tentative_archs)
      for arch in tentative_archs:
        if not clazz.arch_is_valid(arch, system):
          raise ValueError('Invalid arch: %s' % (arch))
      return sorted(tentative_archs)

  @classmethod
  def _determine_archs_linux(clazz, system, tentative_archs):
    if tentative_archs == 'default':
      return clazz.DEFAULT_ARCHS[system]
    if tentative_archs in clazz.VALID_ARCHS[system]:
      return [ tentative_archs ]
    if len(tentative_archs) != 1:
      raise ValueError('Invalid linux arch: %s' % (str(tentative_archs)))
    if tentative_archs[0] in clazz.VALID_ARCHS[system]:
      return tentative_archs
    raise ValueError('Invalid linux arch: %s' % (str(tentative_archs)))

  @classmethod
  def arch_is_valid(clazz, arch, system):
    if system not in build_system.SYSTEMS:
      raise ValueError('Unknown system: %d' % (system))
    return arch in clazz.VALID_ARCHS[system]

  @classmethod
  def archs_to_string(clazz, archs, delimiter = ','):
    return delimiter.join(sorted(archs))

  @classmethod
  def parse_archs(clazz, system, s):
    if s.lower() == 'default':
      return clazz.DEFAULT_ARCHS[system]
    archs = s.split(',')
    for arch in archs:
      if not clazz.arch_is_valid(arch, system):
        raise ValueError('Invalid arch \"%s\" for system \"%s\"' % (arch, system))
    return sorted(archs)

  @classmethod
  def arch_is_known(clazz, arch):
    return arch in clazz.KNOWN_ARCHS
