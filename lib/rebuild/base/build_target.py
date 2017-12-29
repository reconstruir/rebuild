#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.compat import with_metaclass
from bes.system import host
from bes.common import check, dict_util, variable, string_util

from .build_arch import build_arch
from .build_level import build_level
from .build_system import build_system

from collections import namedtuple

class build_target(namedtuple('build_target', 'system,distro,level,archs,build_path')):

  DEFAULT = 'default'

  def __new__(clazz, system = DEFAULT, level = DEFAULT, archs = DEFAULT, distro = None):
    system = build_system.parse_system(system)
    level = clazz._determine_level(level)
    archs = build_arch.determine_archs(system, archs)
    distro = clazz._determine_distro(system, distro)
    build_path = clazz._make_build_path(system, distro, archs, level)
    return clazz.__bases__[0].__new__(clazz, system, distro, level, archs, build_path)

  @classmethod
  def _archs_to_string(clazz, archs):
    return build_arch.archs_to_string(archs, delimiter = '-')
  
  @classmethod
  def _determine_level(clazz, tentative_level):
    if tentative_level == clazz.DEFAULT:
      return build_level.DEFAULT_LEVEL
    if not tentative_level in build_level.LEVELS:
      raise RuntimeError('Invalid level: %s' % (tentative_level))
    return tentative_level

  @classmethod
  def _determine_distro(clazz, system, tentative_distro):
    'Distro only gets set when the host platform is linux.'
    if tentative_distro == clazz.DEFAULT:
      if system in [ build_system.LINUX ] and host.SYSTEM == system:
        return host.DISTRO
      return None
    return tentative_distro

  @classmethod
  def _make_build_path(clazz, system, distro, archs, level):
    if distro:
      system = '%s.%s' % (system, distro)
    parts = [ system, clazz._archs_to_string(archs), level ]
    return '/'.join(parts)

  def is_darwin(self):
    return self.system in [ build_system.MACOS, build_system.IOS ]

  def is_macos(self):
    return self.system == build_system.MACOS

  def is_linux(self):
    return self.system == build_system.LINUX

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
      'archs': self._archs_to_string(self.archs),
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
    archs = parts[1]
    level = parts[2]
    distro = None
    if '.' in system:
      system, _, distro = system.partition('.')
    if '-' in archs:
      archs = archs.split('-')
    return clazz(system = system, level = level, archs = archs, distro = distro)
    
check.register_class(build_target)
