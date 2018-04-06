#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import string_util
from rebuild.base import build_system
from bes.compat import ConfigParser
from bes.compat import StringIO
from collections import OrderedDict
from bes.text import comments

class rebuild_manager_config(OrderedDict):

  KEY_PACKAGES = 'packages'
  COMMON_SECTION = 'common'
  
  def __init__(self):
    super(rebuild_manager_config, self).__init__()

  def load_file(self, filename, build_target):
    parser = ConfigParser()
    with open(filename, 'r') as fp:
      parser.readfp(fp)
      self.update(self.__load(parser, build_target))
      
  def load_string(self, s, build_target):
    parser = ConfigParser()
    fp = StringIO(s)
    parser.readfp(fp)
    self.update(self.__load(parser, build_target))

  @classmethod
  def __load(clazz, parser, build_target):
    config = {}
    common = {}
#    if parser.has_section(clazz.COMMON_SECTION):
      
    for section in parser.sections():
      items = parser.items(section)
      assert section not in config
      config[section] = {}
      for key, value in items:
        parsed_key, system = clazz.__parse_key(key)
        clazz.__update_value(config[section], parsed_key, system, value, build_target)
    return config
  
  @classmethod
  def __update_value(clazz, section, key, system, value, build_target):
    if system:
      system = build_system.parse_system(system)
      if system != build_target.system:
        return
    if key == clazz.KEY_PACKAGES:
      packages = clazz.__parse_packages(value)
      section[key] = section.get(key, []) + packages
    else:
      section[key] = value

  @classmethod
  def __parse_key(clazz, key):
    num_dots = key.count('.')
    if num_dots not in [ 0, 1 ]:
      raise RuntimeError('Invalid key: %s' % (key))
    if num_dots == 0:
      return ( key, None )
    key, _, system = key.partition('.')
    return ( key, system )
    
  @classmethod
  def __parse_packages(clazz, s):
    s = comments.strip_line(s, strip_head = True, strip_tail = True)
    return [ token.strip() for token in string_util.split_by_white_space(s) ]
