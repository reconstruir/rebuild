#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.base import build_system, build_level

class CompileFlags(object):

  COMMON_OPTIMIZATION_FLAGS_RELEASE = [ '-O2', '-DNDEBUG' ]
  COMMON_OPTIMIZATION_FLAGS_DEBUG = [ '-g' ]

  DEFAULT_OPTIMIZATION_FLAGS = {
    build_level.DEBUG: {
      build_system.ANDROID: COMMON_OPTIMIZATION_FLAGS_DEBUG,
      build_system.MACOS: COMMON_OPTIMIZATION_FLAGS_DEBUG,
      build_system.IOS: COMMON_OPTIMIZATION_FLAGS_DEBUG,
      build_system.LINUX: COMMON_OPTIMIZATION_FLAGS_DEBUG,
    },
    build_level.RELEASE: {
      build_system.ANDROID: COMMON_OPTIMIZATION_FLAGS_RELEASE,
      build_system.MACOS: COMMON_OPTIMIZATION_FLAGS_RELEASE,
      build_system.IOS: COMMON_OPTIMIZATION_FLAGS_RELEASE,
      build_system.LINUX: COMMON_OPTIMIZATION_FLAGS_RELEASE,
    },
  }

  def __init__(self, level, system,
               cflags = [],
               ldflags = []):
    self.level = level
    self.system = system

    self.cflags = self.__default_cflags(level, system) + cflags
    self.ldflags = self.__default_ldflags(level, system) + ldflags

  def cflags_append(self, cflags):
    assert isinstance(cflags, list)
    self.cflags = self.cflags + cflags

  def cflags_prepend(self, cflags):
    assert isinstance(cflags, list)
    self.cflags = cflags + self.cflags

  def ldflags_append(self, ldflags):
    assert isinstance(ldflags, list)
    self.ldflags = self.ldflags + ldflags

  def ldflags_prepend(self, ldflags):
    assert isinstance(ldflags, list)
    self.ldflags = ldflags + self.ldflags

  @classmethod
  def __default_cflags(clazz, level, system):
    return clazz.DEFAULT_OPTIMIZATION_FLAGS[level][system]

  @classmethod
  def __default_ldflags(clazz, level, system):
    return []

  @classmethod
  def __flatten(clazz, flags):
    return ' '.join(flags)

  def __compute_env(self):
    return {
      'CFLAGS': self.__flatten(self.cflags),
      'LDFLAGS': self.__flatten(self.ldflags),
    }

  @property
  def env(self):
    return self.__compute_env()

  def append(self, flags):
    assert isinstance(flags, CompileFlags)
    self.cflags += flags.cflags
    self.ldflags += flags.ldflags

  @staticmethod
  def combine(*flags):
    result = {}

    result = None

    for i, n in enumerate(flags):
      if not isinstance(n, CompileFlags):
        raise RuntimeError('Argument %d is not CompileFlags' % (i + 1))
      if not result:
        result = CompileFlags(n.level, n.system,
                              cflags = n.cflags,
                              ldflags = n.ldflags)
      else:
        result.append(n)

    return result
