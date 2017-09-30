#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from .build_arch import build_arch
from .build_type import build_type as BT
from .Category import Category
from .System import System

class build_target(object):

  DEFAULT = 'default'
  BUILD_DIR = 'BUILD'

  def __init__(self, system = DEFAULT, build_type = DEFAULT, archs = DEFAULT):
    # Defaults
    self.system = System.parse_system(system)
    self.archs = build_arch.determine_archs(self.system, archs)
    self.build_type = self.__determine_build_type(build_type)

    assert self.build_type in BT.BUILD_TYPES

    if False:
      self.build_name = path.join(self.system,
                                  build_arch.archs_to_string(self.archs, delimiter = '-'),
                                  self.build_type)
    else:
      self.build_name = path.join(self.system,
                                  self.build_type)

    self.target_dir = path.join(self.BUILD_DIR, self.build_name)

  def clone(self, system = None, build_type = None, archs = None):
    'Clone ourselves but override with args that are not None'
    return build_target(system or self.system,
                     build_type or self.build_type,
                     archs or self.archs)

  def __eq__(self, other):
    return self.system == other.system and self.archs == other.archs and self.build_type == other.build_type
    
  def __str__(self):
    return 'system=%s; archs=%s; build_type=%s; build_name=%s' % (self.system,
                                                                  build_arch.archs_to_string(self.archs),
                                                                  self.build_type,
                                                                  self.build_name)
  
  def __determine_build_type(self, tentative_build_type):
    if tentative_build_type == self.DEFAULT:
      return BT.DEFAULT_BUILD_TYPE
    if not tentative_build_type in BT.BUILD_TYPES:
      raise RuntimeError('Invalid build_type: %s' % (tentative_build_type))
    return tentative_build_type

  def is_darwin(self):
    return self.system in [ System.MACOS, System.IOS ]

  def is_macos(self):
    return self.system == System.MACOS

  def is_linux(self):
    return self.system == System.LINUX

  def to_dict(self):
    return {
      'system': self.system,
      'archs': self.archs,
      'build_type': self.build_type,
    }
