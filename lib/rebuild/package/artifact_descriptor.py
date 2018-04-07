#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import check
from rebuild.base import build_target, build_version
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

  @property
  def build_version(self):
    return build_version(self.version, self.revision, self.epoch)
  
  @property
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

check.register_class(artifact_descriptor, include_seq = False)
