#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.compat import with_metaclass
from bes.system import host
from bes.common import check, dict_util, variable, string_util

from .build_arch import build_arch
from .build_level import build_level
from .build_system import build_system

from collections import namedtuple

class build_target(namedtuple('build_target', 'system, distro, distro_version, arch, level, build_path')):

  def __new__(clazz, system, distro, distro_version, arch, level):
    check.check_string(system)
    if distro is not None:
      check.check_string(distro)
    check.check_string(distro_version)
    arch = build_arch.check_arch(arch, system, distro)
    check.check_string(level)
    system = build_system.parse_system(system)
    arch = build_arch.determine_arch(arch, system, distro)
    level = build_level.parse_level(level)
    build_path = clazz._make_build_path(system, distro, distro_version, arch, level)
    return clazz.__bases__[0].__new__(clazz, system, distro, distro_version, arch, level, build_path)

  @classmethod
  def _arch_to_string(clazz, arch):
    return build_arch.join(arch, delimiter = '-')
  
  @classmethod
  def _make_build_path(clazz, system, distro, distro_version, arch, level):
    system_parts = [ system ]
    if distro and distro != system:
      system_parts += [ distro ]
    if distro_version:
      system_parts += [ distro_version ]
    system_path = '-'.join(system_parts)
    parts = [ system_path, clazz._arch_to_string(arch), level ]
    return '/'.join(parts)

  def is_darwin(self):
    return self.system in [ build_system.MACOS, build_system.IOS ]

  def is_macos(self):
    return self.system == build_system.MACOS

  def is_linux(self):
    return self.system == build_system.LINUX

  def is_desktop(self):
    return build_system.is_desktop(self.system)

  def is_mobile(self):
    return build_system.is_mobile(self.system)

  def to_dict(self):
    return {
      'system': self.system,
      'archs': self.archs,
      'level': self.level,
      'distro': self.distro,
    }

  @property
  def binary_format(self):
    if self.system == build_system.LINUX:
      return 'elf'
    elif self.system == build_system.LINUX:
      return 'macho'
    else:
      return None

  def parse_expression(self, expression):
    variables = {
      'system': self.system,
      'arch': self._arch_to_string(self.arch),
      'level': self.level,
      'distro': self.distro or 'None',
    }
    dict_util.quote_strings(variables)
    exp_with_vars = variable.substitute(expression, variables)
    constants = {
      'MACOS': 'macos',
      'LINUX': 'linux',
      'RELEASE': 'release',
      'DEBUG': 'debug',
      'RASPBIAN': 'raspbian',
    }
    dict_util.quote_strings(constants)
    exp_with_consts = string_util.replace(exp_with_vars, constants, word_boundary = True)
    return eval(exp_with_consts)

  @classmethod
  def parse_path(clazz, s):
    parts = s.split('/')
    if len(parts) != 3:
      raise ValueError('Invalid build path: %s' % (s))
    system = parts[0]
    arch = parts[1]
    level = parts[2]
    system, distro, distro_version = clazz._parse_system(system)
    arch = build_arch.split(arch, delimiter = '-')
    return clazz(system, distro, distro_version, arch, level)

  @classmethod
  def _parse_system(clazz, s):
    parts = s.split('-')
    if len(parts) < 1:
      raise ValueError('Invalid system: %s' % (s))
    distro = ''
    distro_version = ''
    system = parts.pop(0)
    if len(parts) == 1:
      distro_version = parts[0]
    elif len(parts) == 2:
      distro = parts[0]
      distro_version = parts[1]
    else:
      raise ValueError('Invalid system: %s' % (s))
    return system, distro, distro_version

  @classmethod
  def make_host_build_target(clazz, level = build_level.RELEASE):
    return clazz(host.SYSTEM, host.DISTRO, host.VERSION, ( host.ARCH, ), level)
  
check.register_class(build_target)
