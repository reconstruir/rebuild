#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class build_type(object):

  DEBUG = 'debug'
  RELEASE = 'release'
  DEFAULT_BUILD_TYPE = RELEASE
  BUILD_TYPES = [ DEBUG, RELEASE ]

  @classmethod
  def build_type_is_valid(clazz, build_type):
    return build_type in clazz.BUILD_TYPES

  @classmethod
  def parse_build_type(clazz, s):
    slower = s.lower()
    if slower == 'default':
      return clazz.DEFAULT_BUILD_TYPE
    elif slower == clazz.RELEASE:
      return clazz.RELEASE
    elif slower == clazz.DEBUG:
      return  clazz.DEBUG
    else:
      raise RuntimeError('Invalid build_type \"%s\"' % (s))
