
#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, platform
from .System import System
from bes.common import string_util

class build_arch(object):

  ARMV7 = 'armv7'
  ARM64 = 'arm64'
  I386 = 'i386'
  X86_64 = 'x86_64'

  ARCHS = {
    System.ANDROID: [ ARMV7 ],
    # FIXME: fix this when multiarch finally works
    #System.MACOS: [ I386, X86_64 ],
    System.MACOS: [ X86_64 ],
    System.IOS: [ ARM64, ARMV7 ],
    System.IOS_SIM: [ I386, X86_64 ],
    System.LINUX: [],
  }

  DEFAULT_ARCHS = copy.deepcopy(ARCHS)

  KNOWN_ARCHS = [ ARMV7, ARM64, I386, X86_64 ]

  HOST_ARCH = platform.machine()
  # deal with armv7l, armv7b
  if HOST_ARCH.startswith('armv7'):
    HOST_ARCH = ARMV7
  if not HOST_ARCH in KNOWN_ARCHS:
    raise RuntimeError('Unknown host arch: %s' % (HOST_ARCH))
  
  @classmethod
  def determine_archs(clazz, system, tentative_archs):
    result = []
    if system == System.LINUX:
      python_machine = platform.machine()
      if python_machine in [ 'x86_64' ]:
        result = [ clazz.X86_64 ]
      elif python_machine.startswith('armv7'):
        result = [ clazz.ARMV7 ]
      return sorted(result)
    else:
      if not tentative_archs or tentative_archs == 'default':
        return clazz.ARCHS[system]
      if string_util.is_string(tentative_archs):
        return clazz.parse_archs(system, tentative_archs)
      for arch in tentative_archs:
        if not clazz.arch_is_valid(arch, system):
          raise RuntimeError('Invalid arch: %s' % (arch))
      return sorted(tentative_archs)
  
  @classmethod
  def arch_is_valid(clazz, arch, system):
    if system not in System.SYSTEMS:
      raise RuntimeError('Unknown system: %d' % (system))
    return arch in clazz.ARCHS[system]

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
        raise RuntimeError('Invalid arch \"%s\" for system \"%s\"' % (arch, System.system_to_string(system)))
    return sorted(archs)

  @classmethod
  def arch_is_known(clazz, arch):
    return arch in clazz.KNOWN_ARCHS
