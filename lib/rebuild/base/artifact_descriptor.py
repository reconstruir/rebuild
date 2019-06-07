#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common.check import check
from bes.common.json_util import json_util
from bes.common.string_util import string_util
from bes.common.tuple_util import tuple_util
from bes.property.cached_property import cached_property
from bes.archive.archive_extension import archive_extension
from bes.compat.cmp import cmp
from bes.fs.file_util import file_util

from .build_arch import build_arch
from .build_target import build_target
from .build_version import build_version
from .package_descriptor import package_descriptor

class artifact_descriptor(namedtuple('artifact_descriptor', 'name, version, revision, epoch, system, level, arch, distro, distro_version_major, distro_version_minor')):

  def __new__(clazz, name, version, revision, epoch, system, level,
              arch, distro, distro_version_major, distro_version_minor):
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
    distro = build_target.resolve_distro(distro)
    check.check_string(distro_version_major)
    distro_version_major = build_target.resolve_distro_version(distro_version_major)
    check.check_string(distro_version_minor)
    distro_version_minor = build_target.resolve_distro_version(distro_version_minor)
    return clazz.__bases__[0].__new__(clazz, name, version, revision, epoch,
                                      system, level, arch, distro,
                                      distro_version_major, distro_version_minor)

  def __str__(self):
    arch_str = ','.join(self.arch)
    return '%s;%s;%s;%s;%s;%s;%s;%s;%s;%s' % (self.name, self.version, self.revision, self.epoch, self.system, self.level,
                                              arch_str, self.distro, self.distro_version_major, self.distro_version_minor)

  def __hash__(self):
    return hash(str(self))
  
  @cached_property
  def build_version(self):
    return build_version(self.version, self.revision, self.epoch)
  
  @cached_property
  def build_target(self):
    return build_target(self.system, self.distro, self.distro_version_major, self.distro_version_minor, self.arch, self.level)

  @cached_property
  def sql_table_name(self):
    return string_util.replace_punctuation(str(self), '_')

  @cached_property
  def sql_tuple(self):
    return (
      self.name,
      self.version,
      self.revision,
      self.epoch,
      self.system,
      self.distro,
      self.distro_version_major,
      self.distro_version_minor,
      self._sql_encode_string_list(self.arch),
      self.level,
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

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
  @classmethod
  def parse(clazz, s):
    parts = s.split(';')
    if len(parts) != len(clazz._fields):
      raise ValueError('Invalid artifact descriptor: %s' % (s))
    return artifact_descriptor(*parts)

  @classmethod
  def parse_artifact_path(clazz, artifact_path):
    build_path = path.dirname(artifact_path)
    filename = path.basename(artifact_path)
    bt = build_target.parse_path(build_path)
    ext = archive_extension.extension_for_filename(filename)
    nv = string_util.remove_tail(filename, '.' + ext)
    pd = package_descriptor.parse(nv)
    return artifact_descriptor(pd.name, pd.version.upstream_version, pd.version.revision,
                               pd.version.epoch, bt.system, bt.level, bt.arch, bt.distro,
                               bt.distro_version_major, bt.distro_version_minor)

  @classmethod
  def compare(clazz, a1, a2):
    check.check_artifact_descriptor(a1)
    check.check_artifact_descriptor(a2)
    t1 = ( a1.name, a1.system, a1.level, a1.arch, a1.distro, a1.distro_version_major, a1.distro_version_minor )
    t2 = ( a2.name, a2.system, a2.level, a2.arch, a2.distro, a2.distro_version_major, a2.distro_version_minor )
    result = cmp(t1, t2)
    if result != 0:
      return result
    return build_version.compare(a1.build_version, a2.build_version)

  def __lt__(self, other):
    check.check_artifact_descriptor(other)
    return self.compare(self, other) < 0

  @classmethod
  def make_from_package_descriptor(clazz, pdesc, build_target):
    check.check_package_descriptor(pdesc)
    check.check_build_target(build_target)
    return artifact_descriptor(pdesc.name, pdesc.version.upstream_version,
                               pdesc.version.revision, pdesc.version.epoch,
                               build_target.system, build_target.level, build_target.arch,
                               build_target.distro, build_target.distro_version_major,
                               build_target.distro_version_minor)

  def clone_without_distro(self):
    mutations = {}
    if self.distro:
      mutations = { 'distro': '', 'distro_version_major': '', 'distro_version_minor': '' }
    return self.clone(mutations = mutations)
  
check.register_class(artifact_descriptor, include_seq = False)
