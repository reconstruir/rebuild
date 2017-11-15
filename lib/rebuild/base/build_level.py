#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class build_level(object):

  DEBUG = 'debug'
  RELEASE = 'release'
  DEFAULT_BUILD_TYPE = RELEASE
  BUILD_TYPES = [ DEBUG, RELEASE ]

  @classmethod
  def build_level_is_valid(clazz, build_level):
    return build_level in clazz.BUILD_TYPES

  @classmethod
  def parse_build_level(clazz, s):
    slower = s.lower()
    if slower == 'default':
      return clazz.DEFAULT_BUILD_TYPE
    elif slower == clazz.RELEASE:
      return clazz.RELEASE
    elif slower == clazz.DEBUG:
      return  clazz.DEBUG
    else:
      raise RuntimeError('Invalid build_level \"%s\"' % (s))