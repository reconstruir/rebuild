#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from collections import namedtuple
from bes.common import cached_property, check, string_util
from rebuild.base import build_arch, build_level, build_system, build_target, build_version, package_descriptor
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
    distro = distro or ''
    check.check_string(distro)
    return clazz.__bases__[0].__new__(clazz, name, version, revision, epoch, system, level, archs, distro)

  def __str__(self):
    return '%s;%s;%s;%s;%s;%s;%s;%s' % (self.name, self.version, self.revision, self.epoch, self.system, self.level,
                                        ','.join(self.archs), self.distro)

  @cached_property
  def sql_table_name(self):
    return string_util.replace_punctuation(str(self), '_')

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
      self.distro,
    )

  @classmethod
  def parse_artifact_filename(clazz, filename):
    parts = filename.split(os.sep)
    if len(parts) != 4:
      raise ValueError('not a valid artifact: %s' % (filename))
    system = parts[0]
    if not build_system.system_is_valid(system):
      raise ValueError('invalid system \"%s\" for %s' % (system, filename))
    archs = parts[1].split('-')
    for arch in archs:
      if not build_arch.arch_is_valid(arch, system):
        raise ValueError('invalid arch \"%s\" for %s' % (arch, filename))
    level = parts[2]
    if not build_level.level_is_valid(level):
      raise ValueError('invalid level \"%s\" for %s' % (level, filename))
    desc = parts[3].replace('.tar.gz', '')
    pdesc = package_descriptor.parse(desc)
    return clazz(pdesc.name,
                 pdesc.version.upstream_version,
                 pdesc.version.revision,
                 pdesc.version.epoch,
                 system,
                 level,
                 archs,
                 None)

  @cached_property
  def full_name(self):
    return self.make_full_name_str(self.name, self.build_version)

  @classmethod
  def make_full_name_str(clazz, name, version):
    return '%s%s%s' % (name, '-', str(version))

check.register_class(artifact_descriptor, include_seq = False)
