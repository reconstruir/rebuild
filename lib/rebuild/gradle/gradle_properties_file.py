#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.system import log
from bes.common import check
from bes.properties.properties_file import properties_file

class gradle_properties_file(object):

  @classmethod
  def read(clazz, filename):
    return properties_file.read(filename, style = 'java')

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
