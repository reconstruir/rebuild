#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from collections import namedtuple
from bes.common import check, cached_property
from rebuild.base import build_arch, build_level, build_system, build_target, build_version
from .util import util

class artifact_descriptor(namedtuple('artifact_descriptor', 'name, version, revision, epoch, system, level, archs, distro')):

  WHERE_EXPRESSION = 'name=? and version=? and revision=? and epoch=? and system=? and level=? and archs=? and distro=?'
  
  def __new__(clazz, name, version, revision, epoch, system, level, archs, distro):
    check.check_string(name)
    check.check_string(version)
    check.check_int(revision)
    check.check_int(epoch)
    check.check_string(system)
    check.check_string(level)
    check.check_string_seq(archs)
    if distro:
      check.check_string(distro)
    return clazz.__bases__[0].__new__(clazz, name, version, revision, epoch, system, level, archs, distro)

  def __str__(self):
    return '%s,%s,%s,%s,%s,%s,%s,%s' % (self.name, self.version, self.revision, self.epoch, self.system, self.level, self.archs, self.distro)

  @cached_property
  def build_version(self):
    return build_version(self.version, self.revision, self.epoch)
  
  @cached_property
  def build_target(self):
    return build_target(system = self.system, level = self.level, archs = self.archs, distro = self.distro)

  def to_sql_tuple(self):
    return (
      self.name,
      self.version,
      self.revision,
      self.epoch,
      self.system,
      self.level,
      util.sql_encode_string_list(self.archs, quoted = False),
      self.distro
    )

  @classmethod
  def parse_artifact_filename(clazz, filename):
    parts = filename.split(os.sep)
    if len(parts) != 4:
      raise ValueError('not a valid artifact: %s' % (filename))
    system = parts[0]
    if not build_system.system_is_valid(system):
      raise ValueError('invalid system \"%s\" for %s' % (system, filename))
    archs = parts[1]
    if not build_level.level_is_valid(level):
      raise ValueError('invalid level \"%s\" for %s' % (level, filename))
    level = parts[2]
    if not build_level.level_is_valid(level):
      raise ValueError('invalid level \"%s\" for %s' % (level, filename))
    fn = parts[3]
    
    print('parts: %s ' % (parts))
    return None
  
check.register_class(artifact_descriptor, include_seq = False)
