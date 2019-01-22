#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import json
from collections import namedtuple
from bes.common import cached_property, check, json_util, string_util, tuple_util
from rebuild.base import artifact_descriptor,  build_arch, build_target, build_version, package_descriptor, requirement_list

from .package_manifest import package_manifest

class package_metadata(namedtuple('package_metadata', 'format_version, filename, name, version, revision, epoch, system, level, arch, distro, distro_version_major, distro_version_minor, requirements, properties, manifest')):

  FORMAT_VERSION = 2
  
  def __new__(clazz, format_version, filename, name, version, revision, epoch, system,
              level, arch, distro, distro_version_major, distro_version_minor, requirements,
              properties, manifest):
    assert format_version == clazz.FORMAT_VERSION
    check.check_string(filename)
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
    check.check_string(distro, allow_none = True)
    distro = distro or ''
    check.check_string(distro_version_major)
    check.check_string(distro_version_minor)
    if check.is_string(requirements):
      requirements = requirement_list.parse(requirements)
    requirements = requirements or requirement_list()
    check.check_requirement_list(requirements)
    properties = properties or {}
    check.check_dict(properties)
    check.check_package_manifest(manifest)
    return clazz.__bases__[0].__new__(clazz, format_version, filename, name, version,
                                      revision, epoch, system, level, arch,
                                      distro, distro_version_major, distro_version_minor,
                                      requirements, properties, manifest)

  def __hash__(self):
    return hash(str(self))
  
  @cached_property
  def build_version(self):
    return build_version(self.version, self.revision, self.epoch)
  
  @cached_property
  def package_descriptor(self):
    return package_descriptor(self.name, str(self.build_version), properties = self.properties, requirements = self.requirements)

  @cached_property
  def artifact_descriptor(self):
    return artifact_descriptor(self.name, self.version, self.revision, self.epoch,
                               self.system, self.level, self.arch, self.distro,
                               self.distro_version_major, self.distro_version_minor)

  @cached_property
  def build_target(self):
    return build_target(self.system, self.distro, self.distro_version_major, self.distro_version_minor, self.arch, self.level)
    
  def to_json(self):
    return json_util.to_json(self.to_simple_dict(), indent = 2, sort_keys = True)

  @classmethod
  def parse_json(clazz, text):
    o = json.loads(text)
    format_version = o.get('_format_version', 1)
    if format_version == 2:
      return clazz._parse_dict_v2(o)
    else:
      raise ValueError('invalid format_version: %s' % (format_version))

  @classmethod
  def _parse_dict_v2(clazz, o):
    return package_metadata(clazz.FORMAT_VERSION,
                            o['filename'],
                            o['name'],
                            o['version'],
                            o['revision'],
                            o['epoch'],
                            o['system'],
                            o['level'],
                            tuple(o['arch']),
                            o['distro'],
                            o['distro_version_major'],
                            o['distro_version_minor'],
                            requirement_list.from_string_list(o['requirements']),
                            o['properties'],
                            package_manifest.parse_dict(o['manifest']))
  
  def to_simple_dict(self):
    'Return a simplified dict suitable for json encoding.'
    return {
      '_format_version': self.format_version,
      'name': self.name,
      'filename': self.filename,
      'version': self.version,
      'revision': self.revision,
      'epoch': self.epoch,
      'system': self.system,
      'level': self.level,
      'arch': self.arch,
      'distro': self.distro,
      'distro_version_major': self.distro_version_major,
      'distro_version_minor': self.distro_version_minor,
      'requirements': self.requirements.to_string_list(),
      'properties': self.properties,
      'manifest': self.manifest.to_simple_dict(),
    }

  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)
  
  def mutate_filename(self, filename):
    return self.clone({ 'filename': filename })

  @cached_property
  def full_name(self):
    return self.make_full_name_str(self.name, self.build_version)

  @classmethod
  def make_full_name_str(clazz, name, version):
    return '%s%s%s' % (name, '-', str(version))

  @classmethod
  def compare(clazz, p1, p2):
    check.check_package_metadata(p1)
    check.check_package_metadata(p2)
    t1 = ( p1.format_version, p1.filename, p1.name, p1.system, p1.level, p1.arch, p1.distro, p1.distro_version_major, p1.distro_version_minor, p1.requirements, p1.properties, p1.manifest )
    t2 = ( p2.format_version, p2.filename, p2.name, p2.system, p2.level, p2.arch, p2.distro, p2.distro_version_major, p2.distro_version_minor, p2.requirements, p2.properties, p2.manifest )
    result = cmp(t1, t2)
    if result != 0:
      return result
    return build_version.compare(p1.build_version, p2.build_version)

  def __lt__(self, other):
    check.check_package_metadata(other)
    return self.compare(self, other) < 0

  @classmethod
  def make_from_artifact_descriptor(clazz, adesc, filename):
    '''
    Make a package_decriptor from an artifact_descriptor.
    requirements, properties and manifest will be missing.
    '''
    check.check_artifact_descriptor(adesc)
    check.check_string(filename)
    return package_metadata(clazz.FORMAT_VERSION,
                            filename,
                            adesc.name,
                            adesc.version,
                            adesc.revision,
                            adesc.epoch,
                            adesc.system,
                            adesc.level,
                            adesc.arch,
                            adesc.distro,
                            adesc.distro_version_major,
                            adesc.distro_version_minor,
                            None,
                            None,
                            package_manifest(None, None))
    
check.register_class(package_metadata, include_seq = False)
