#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.common import cached_property, check, json_util, string_util
from bes.compat import cmp

from .build_arch import build_arch
from .build_target import build_target
from .build_version import build_version

class artifact_descriptor(namedtuple('artifact_descriptor', 'name, version, revision, epoch, system, level, arch, distro, distro_version')):

  WHERE_EXPRESSION = 'name=? and version=? and revision=? and epoch=? and system=? and level=? and arch=? and distro=? and distro_version=?'
  
  def __new__(clazz, name, version, revision, epoch, system, level,
              arch, distro, distro_version):
    check.check_string(name)
    check.check_string(version)
    revision = int(revision)
    check.check_int(revision)
    epoch = int(epoch)
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

  def __hash__(self):
    return hash(str(self))
  
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
      self._sql_encode_string_list(self.arch),
      self.distro,
      self.distro_version,
    )

  @classmethod
  def _sql_encode_string_list(clazz, l):
    check.check_string_seq(l)
    s = json_util.to_json(l)
    return s if s is not None else 'null'
  
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

  def clone_with_mutations(self, mutations):
    l = list(self)
    for field, value in mutations.items():
      i = self._fields.index(field)
      l[i] = value
    return self.__class__(*l)

  @classmethod
  def parse(clazz, s):
    parts = s.split(';')
    if len(parts) != 9:
      raise ValueError('Invalid artifact descriptor: %s' % (s))
    return clazz(*parts)

  @classmethod
  def compare(clazz, a1, a2):
    check.check_artifact_descriptor(a1)
    check.check_artifact_descriptor(a2)
    t1 = ( a1.name, a1.system, a1.level, a1.arch, a1.distro, a1.distro_version )
    t2 = ( a2.name, a2.system, a2.level, a2.arch, a2.distro, a2.distro_version )
    result = cmp(t1, t2)
    if result != 0:
      return result
    return build_version.compare(a1.build_version, a2.build_version)

  def __lt__(self, other):
    check.check_artifact_descriptor(other)
    return self.compare(self, other) < 0
  
check.register_class(artifact_descriptor, include_seq = False)
