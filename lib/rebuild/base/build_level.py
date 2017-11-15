#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class build_level(object):

  DEBUG = 'debug'
  RELEASE = 'release'
  DEFAULT_LEVEL = RELEASE
  LEVELS = [ DEBUG, RELEASE ]

  @classmethod
  def level_is_valid(clazz, build_level):
    return build_level in clazz.LEVELS

  @classmethod
  def parse_level(clazz, s):
    slower = s.lower()
    if slower == 'default':
      return clazz.DEFAULT_LEVEL
    elif slower == clazz.RELEASE:
      return clazz.RELEASE
    elif slower == clazz.DEBUG:
      return  clazz.DEBUG
    else:
      raise RuntimeError('Invalid build_level \"%s\"' % (s))
