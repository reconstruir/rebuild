#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import host
from bes.common import algorithm, string_util

class System(object):

  # Systems supported
  ANDROID = 'android'
  IOS = 'ios'
  IOS_SIM = 'ios_sim'
  LINUX = host.LINUX
  MACOS = host.MACOS

  # System masks
  NONE = 'none'
  ALL = 'all'
  MOBILE = 'android|ios'
  DESKTOP = 'macos|linux'
  DARWIN = 'macos|ios|ios_sim'
  HOST = host.SYSTEM
  DEFAULT = HOST
  
  DELIMITER = '|'

  SYSTEMS = [ ANDROID, IOS, IOS_SIM, LINUX, MACOS ]

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
    return clazz.DELIMITER.join(clazz.__resolve_mask_to_list(s))

  @classmethod
  def __resolve_mask_to_list(clazz, s):
    assert string_util.is_string(s)
    s = s.lower()
    s = clazz.ALIASES.get(s, s)
    parts = [ part for part in clazz.mask_split(s) if part ]
    result = []
    for part in parts:
      result.extend(clazz.__resolve_mask_part(part))
    result = sorted(algorithm.unique(result))
    if not result:
      return [ clazz.NONE ]
    return result

  @classmethod
  def __resolve_mask_part(clazz, part):
    assert string_util.is_string(part)
    assert clazz.DELIMITER not in part
    part = clazz.ALIASES.get(part, part)
    if clazz.DELIMITER in part:
      return clazz.__resolve_mask_to_list(part)
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
    parts = clazz.mask_split(mask)
    for part in parts:
      if not clazz.system_is_valid(part):
        return False
    return True

  @classmethod
  def parse_system(clazz, s):
    if not string_util.is_string(s):
      raise RuntimeError('Not a string: %s' % (str(s)))
    systems = clazz.mask_split(clazz.resolve_mask(s))
    if len(systems) != 1:
      raise RuntimeError('Invalid system: %s' % (str(s)))
    return systems[0]
  
  @classmethod
  def system_is_valid(clazz, system):
    return system in clazz.SYSTEMS

  @classmethod
  def mask_matches(clazz, mask, system):
    return system in clazz.__resolve_mask_to_list(mask)
