#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import cached_property, check, string_util
from rebuild.base import build_arch, build_target, build_version
from .util import util

class artifact_descriptor(namedtuple('artifact_descriptor', 'name, version, revision, epoch, system, level, arch, distro, distro_version')):

  WHERE_EXPRESSION = 'name=? and version=? and revision=? and epoch=? and system=? and level=? and arch=? and distro=? and distro_version=?'
  
  def __new__(clazz, name, version, revision, epoch, system, level,
              arch, distro, distro_version):
    check.check_string(name)
    check.check_string(version)
    check.check_int(revision)
    check.check_int(epoch)
    check.check_string(system)
    check.check_string(level)
    arch = build_arch.check_arch(arch, system, distro)
    check.check_tuple(arch)
    check.check_string(distro)
    check.check_string(distro_version)
    return clazz.__bases__[0].__new__(clazz, name, version, revision, epoch,
                                      system, level, arch, distro, distro_version)

  def __str__(self):
    arch_str = ','.join(self.arch)
    return '%s;%s;%s;%s;%s;%s;%s;%s;%s' % (self.name, self.version, self.revision, self.epoch, self.system, self.level,
                                           arch_str, self.distro, self.distro_version)

  @cached_property
  def sql_table_name(self):
    return string_util.replace_punctuation(str(self), '_')

  @cached_property
  def build_version(self):
    return build_version(self.version, self.revision, self.epoch)
  
  @cached_property
  def build_target(self):
    return build_target(self.system, self.distro, self.distro_version, self.arch, self.level)

  def to_sql_tuple(self):
    return (
      self.name,
      self.version,
      self.revision,
      self.epoch,
      self.system,
      self.level,
      util.sql_encode_string_list(self.arch, quoted = False),
      self.distro,
      self.distro_version,
    )

  @cached_property
  def full_name(self):
    return self.make_full_name_str(self.name, self.build_version)

  @classmethod
  def make_full_name_str(clazz, name, version):
    return '%s%s%s' % (name, '-', str(version))

  def clone_with_mutation(self, field, value):
    i = self._fields.index(field)
    l = list(self)
    l[i] = value
    return self.__class__(*l)

check.register_class(artifact_descriptor, include_seq = False)
