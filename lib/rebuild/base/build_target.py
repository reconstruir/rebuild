#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.compat import with_metaclass
from bes.system.host import host
from bes.common.check import check
from bes.common.dict_util import dict_util
from bes.common.string_util import string_util
from bes.common.tuple_util import tuple_util
from bes.common.variable import variable
from bes.property.cached_property import cached_property

from .build_arch import build_arch
from .build_level import build_level
from .build_system import build_system

from collections import namedtuple

class build_target(namedtuple('build_target', 'system, distro, distro_version_major, distro_version_minor, arch, level')):

  def __new__(clazz, system, distro, distro_version_major, distro_version_minor, arch, level):
    check.check_string(system)
    check.check_string(distro, allow_none = True)
    distro = clazz.resolve_distro(distro)
    check.check_string(distro_version_major, allow_none = True)
    check.check_string(distro_version_minor, allow_none = True)
    arch = build_arch.check_arch(arch, system, distro)
    check.check_string(level)
    system = build_system.parse_system(system)
    arch = build_arch.determine_arch(arch, system, distro)
    level = build_level.parse_level(level)
    distro_version_major = clazz.resolve_distro_version(distro_version_major)
    distro_version_minor = clazz.resolve_distro_version(distro_version_minor)
    if system != host.LINUX and distro not in [ '', 'any', 'none' ]:
      raise ValueError('distro for \"%s\" should be empty/none instead of \"%s\"' % (system, distro))
    if system == host.LINUX and not distro:
      if distro_version_major:
        raise ValueError('no distro so distro_version_major should be empty/none instead of: %s' % (distro_version_major))
      if distro_version_minor:
        raise ValueError('no distro so distro_version_minor should be empty/none instead of: %s' % (distro_version_minor))
    return clazz.__bases__[0].__new__(clazz, system, distro, distro_version_major, distro_version_minor, arch, level)

  def __str__(self):
    return self.build_path
  
  @cached_property
  def build_path(self):
    return self._make_build_path(self.system, self.distro, self.distro_version_major, self.distro_version_minor, self.arch, self.level)    
  
  @classmethod
  def _arch_to_string(clazz, arch):
    return build_arch.join(arch, delimiter = '-')
  
  @classmethod
  def _make_build_path(clazz, system, distro, distro_version_major, distro_version_minor, arch, level):
    system_parts = [ system ]
    if distro and distro != system:
      system_parts += [ distro ]
    version_parts = []
    if distro_version_major:
      version_parts.append(distro_version_major)
    if distro_version_minor:
      version_parts.append(distro_version_minor)
    version = '.'.join(version_parts)
    if version:
      system_parts += [ version ]
    system_path = '-'.join(system_parts)
    parts = [ system_path, clazz._arch_to_string(arch), level ]
    return '/'.join(parts)

  def is_darwin(self):
    return self.system in [ build_system.MACOS, build_system.IOS ]

  def is_macos(self):
    return self.system == build_system.MACOS

  def is_linux(self):
    return self.system == build_system.LINUX

  def is_desktop(self):
    return build_system.is_desktop(self.system)

  def is_mobile(self):
    return build_system.is_mobile(self.system)

  def to_dict(self):
    return self._asdict()

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
      'arch': self._arch_to_string(self.arch),
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
    num_parts = len(parts)
    if num_parts < 2:
      raise ValueError('Invalid build path: %s' % (s))
    system = parts[0]
    arch = parts[1]
    level = parts[2] if num_parts > 2 else 'release'
    system, distro, distro_version_major, distro_version_minor = clazz._parse_system(system)
    arch = build_arch.split(arch, delimiter = '-')
    return build_target(system, distro, distro_version_major, distro_version_minor, arch, level)

  @classmethod
  def _parse_system(clazz, s):
    parts = s.split('-')
    if len(parts) < 1:
      raise ValueError('Invalid system: %s' % (s))
    distro = ''
    distro_version_major = ''
    distro_version_minor = None
    system = parts.pop(0)
    if len(parts) == 1:
      distro_version_major, distro_version_minor = clazz._parse_version(parts[0])
    elif len(parts) == 2:
      distro = parts[0]
      distro_version_major, distro_version_minor = clazz._parse_version(parts[1])
    elif len(parts) > 2:
      raise ValueError('Invalid system: %s' % (s))
    return system, distro, distro_version_major, distro_version_minor

  @classmethod
  def _parse_version(clazz, s):
    parts = s.split('.')
    if not parts:
      return None, None
    distro_version_major = parts.pop(0)
    distro_version_minor = parts.pop(0) if parts else None
    return distro_version_major, distro_version_minor
  
  @classmethod
  def make_host_build_target(clazz, level = build_level.RELEASE):
    if host.SYSTEM == host.LINUX:
      return build_target(host.SYSTEM, host.DISTRO, host.VERSION_MAJOR, None, ( host.ARCH, ), level)
    elif host.SYSTEM == host.MACOS:
      return build_target(host.SYSTEM, None, host.VERSION_MAJOR, None, ( host.ARCH, ), level)
    elif host.SYSTEM == host.WINDOWS:
      return build_target(host.SYSTEM, None, host.VERSION_MAJOR, None, ( host.ARCH, ), level)
    else:
      return build_target(host.SYSTEM, None, host.VERSION_MAJOR, host.VERSION_MINOR, ( host.ARCH, ), level)
      
  def clone(self, mutations = None):
    return tuple_util.clone(self, mutations = mutations)

  @classmethod
  def resolve_distro_version(clazz, version):
    if check.is_string(version):
      if version.lower() == 'none':
        version = ''
    elif version is None:
      version = ''
    return version
  
  @classmethod
  def resolve_distro(clazz, distro):
    if check.is_string(distro):
      if distro.lower() == 'none':
        distro = ''
    elif distro is None:
      distro = ''
    return distro
  
  def match(self, other):
    'Return True if self matches other build_target'
    check.check_build_target(other)
    return \
      (other.system == 'any' or (self.system == other.system)) and \
      (other.distro == 'any' or (self.distro == other.distro)) and \
      (other.distro_version_major == 'any' or (self.distro_version_major == other.distro_version_major)) and \
      (other.distro_version_minor == 'any' or (self.distro_version_minor == other.distro_version_minor)) and \
      (other.arch == 'any' or (self.arch == other.arch)) and \
      (other.level == 'any' or (self.level == other.level))
  
check.register_class(build_target)
