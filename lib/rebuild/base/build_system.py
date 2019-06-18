#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host
from bes.common.algorithm import algorithm
from bes.common.check import check
from bes.common.string_util import string_util

class build_system(object):

  # Systems supported
  ANDROID = 'android'
  IOS = 'ios'
  IOS_SIM = 'ios_sim'
  LINUX = host.LINUX
  MACOS = host.MACOS
  WINDOWS = host.WINDOWS

  # System masks
  NONE = 'none'
  ALL = 'all'
  MOBILE = 'android|ios'
  DESKTOP = 'macos|linux|windows'
  DARWIN = 'macos|ios|ios_sim'
  HOST = host.SYSTEM
  HOST_DISTRO = host.DISTRO
  HOST_VERSION_MAJOR = host.VERSION_MAJOR
  HOST_VERSION_MINOR = host.VERSION_MINOR
  DEFAULT = HOST
  
  DELIMITER = '|'

  SYSTEMS = [ ANDROID, IOS, IOS_SIM, LINUX, MACOS, WINDOWS ]

  RASPBIAN = host.RASPBIAN
  
  ALIASES = {
    'none': NONE,
    'all': ALL,
    'mobile': MOBILE,
    'desktop': DESKTOP,
    'darwin':  DARWIN,
    'default':  DEFAULT,
  }
  
  @classmethod
  def resolve_mask(clazz, s):
    return clazz.DELIMITER.join(clazz._resolve_mask_to_list(s))

  @classmethod
  def _resolve_mask_to_list(clazz, s):
    assert string_util.is_string(s)
    s = s.lower()
    s = clazz.ALIASES.get(s, s)
    parts = [ part for part in clazz.mask_split(s) if part ]
    result = []
    for part in parts:
      result.extend(clazz._resolve_mask_part(part))
    result = sorted(algorithm.unique(result))
    if not result:
      return [ clazz.NONE ]
    return result

  @classmethod
  def _resolve_mask_part(clazz, part):
    assert string_util.is_string(part)
    assert clazz.DELIMITER not in part
    part = clazz.ALIASES.get(part, part)
    if clazz.DELIMITER in part:
      return clazz._resolve_mask_to_list(part)
    if part == clazz.NONE:
      return []
    elif part == clazz.ALL:
      return clazz.SYSTEMS
    else:
      return [ part ]

  @classmethod
  def mask_split(clazz, mask):
    return mask.split(clazz.DELIMITER)

  @classmethod
  def mask_is_valid(clazz, mask):
    if not string_util.is_string(mask):
      return False
    #parts = clazz.mask_split(mask)
    parts = clazz._resolve_mask_to_list(mask)
    for part in parts:
      if not clazz.system_is_valid(part):
        return False
    return True

  @classmethod
  def parse_system(clazz, s):
    check.check_string(s)
    systems = clazz.mask_split(clazz.resolve_mask(s))
    if len(systems) != 1:
      raise ValueError('Invalid system: {}'.format(str(s)))
    system = systems[0]
    if not system in clazz.SYSTEMS:
      raise ValueError('Invalid system: {}'.format(system))
    return system
  
  @classmethod
  def system_is_valid(clazz, system):
    return system in clazz.SYSTEMS

  @classmethod
  def check_system(clazz, system):
    if not clazz.system_is_valid(system):
      raise ValueError('Invalid system: %s' % (str(system)))

  @classmethod
  def mask_matches(clazz, mask, system):
    resolved_mask = clazz._resolve_mask_to_list(mask)
    if not resolved_mask:
      raise ValueError('Invalid mask: %s - %s' % (str(mask), type(mask)))
    if not clazz.system_is_valid(system):
      raise ValueError('Invalid system: %s - %s' % (str(system), type(system)))
    return system in resolved_mask

  @classmethod
  def is_desktop(clazz, system):
    return clazz.mask_matches(clazz.DESKTOP, system)
  
  @classmethod
  def is_mobile(clazz, system):
    return clazz.mask_matches(clazz.MOBILE, system)
