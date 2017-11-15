#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.system.compat import with_metaclass
from bes.common import check_type

from .build_arch import build_arch
from .build_level import build_level
from .build_system import build_system

from collections import namedtuple

class build_target(namedtuple('build_target', 'system,level,archs,build_path')):

  DEFAULT = 'default'
  
  def __new__(clazz, system = DEFAULT, level = DEFAULT, archs = DEFAULT):
    system = build_system.parse_system(system)
    level = clazz._determine_level(level)
    archs = build_arch.determine_archs(system, archs)
    build_path = path.join(system, build_arch.archs_to_string(archs, delimiter = '-'), level)
    return clazz.__bases__[0].__new__(clazz, system, level, archs, build_path)

  @classmethod
  def _determine_level(clazz, tentative_level):
    if tentative_level == clazz.DEFAULT:
      return build_level.DEFAULT_LEVEL
    if not tentative_level in build_level.LEVELS:
      raise RuntimeError('Invalid level: %s' % (tentative_level))
    return tentative_level

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
    }

  @property
  def binary_format(self):
    if self.system == build_system.LINUX:
      return 'elf'
    elif self.system == build_system.LINUX:
      return 'macho'
    else:
      return None
check_type.register_class(build_target)
