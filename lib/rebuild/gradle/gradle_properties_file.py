#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-


from os import path
from collections import namedtuple

from bes.system import log
from bes.common import check
from bes.properties.properties_file import properties_file

class gradle_properties_file(object):

  _credentials = namedtuple('credentials', 'username, password')
  
  @classmethod
  def read_file(clazz, filename):
    return properties_file.read(filename, style = 'java')

  FILENAME = path.expanduser('.gradle/gradle.properties')
  DEFAULT_FILENAME = path.expanduser('~/{}'.format(FILENAME))
  
  @classmethod
  def read_default_file(clazz):
    'Read ~/.gradle/gradle.properties'
    return clazz.read(clazz.DEFAULT_FILENAME)

  @classmethod
  def default_file_exists(clazz):
    'Read True if ~/.gradle/gradle.properties'
    return path.isfile(clazz.DEFAULT_FILENAME)

  @classmethod
  def _make_filepath(clazz, root_dir = None):
    root_dir = root_dir or path.expanduser('~/')
    return path.join(root_dir, clazz.FILENAME)

  @classmethod
  def load(clazz, root_dir = None):
    p = clazz._make_filepath(root_dir = root_dir)
    return clazz.read_file(p)
    
  @classmethod
  def has_gradle_properties(clazz, root_dir = None):
    p = clazz._make_filepath(root_dir = root_dir)
    return path.isfile(p)

  @classmethod
  def credentials(clazz, root_dir = None):
    props = clazz.load(root_dir = root_dir)
    username = props.get('systemProp.gradle.wrapperUser', None)
    password = props.get('systemProp.gradle.wrapperPassword', None)
    return self._credentials(username, password)
  
  @classmethod
  def username(clazz, root_dir = None):
    return self.credentials(root_dir = root_dir).username
  
  @classmethod
  def password(clazz, root_dir = None):
    return self.credentials(root_dir = root_dir).password
  
log.add_logging(gradle_properties_file, 'gradle_properties_file')