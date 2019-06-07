#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

class build_level(object):

  DEBUG = 'debug'
  RELEASE = 'release'
  ANY = 'any'
  LEVELS = [ DEBUG, RELEASE, ANY ]

  @classmethod
  def level_is_valid(clazz, build_level):
    return build_level in clazz.LEVELS

  @classmethod
  def parse_level(clazz, s):
    slower = s.lower()
    if not slower in clazz.LEVELS:
      raise ValueError('Invalid build_level: %s' % (s))
    return slower

check.register_class(build_level)
    
