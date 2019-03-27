#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.system import log
from bes.common import check
from bes.fs import file_util
from bes.key_value import key_value, key_value_list
from bes.text import text_line_parser

class gradle_properties_file(object):

  @classmethod
  def read(clazz, filename):
    check.check_string(filename)
    content = file_util.read(filename)
    lines = text_line_parser.parse_lines(content)
    result = key_value_list()
    for line in lines:
      result.append(key_value.parse(line))
    return result.to_dict()

  DEFAULT_FILENAME = path.expanduser('~/.gradle/gradle.properties')
  @classmethod
  def read_default_file(clazz):
    'Read ~/.gradle/gradle.properties'
    return clazz.read(clazz.DEFAULT_FILENAME)

  @classmethod
  def default_file_exists(clazz):
    'Read True if ~/.gradle/gradle.properties'
    return path.isfile(clazz.DEFAULT_FILENAME)
    
log.add_logging(gradle_properties_file, 'gradle_properties_file')
