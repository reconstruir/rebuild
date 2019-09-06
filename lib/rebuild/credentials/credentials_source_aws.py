#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.compat.ConfigParser import ConfigParser

from .credentials import credentials
from .credentials_source import credentials_source

class credentials_source_aws(credentials_source):

  DEFAULT_FILENAME = path.expanduser('~/.aws/credentials')
  
  def __init__(self, filename = DEFAULT_FILENAME):
    self._filename = filename
  
  #@abstractmethod
  def is_valid(self):
    if not path.isfile(self._filename):
      return False
    d = self._read_file(self._filename)
    return bool(d)

  #@abstractmethod
  def credentials(self):
    d = self._read_file(self._filename)
    if not d:
      return None
    return credentials(self._filename, **d)
  
  @classmethod
  def _read_file(clazz, filename):
    parser = ConfigParser()
    with open(filename, 'r') as fin:
      try:
        return clazz._read_section(parser, fin)
      except Exception as ex:
        return None
        
  @classmethod
  def _read_section(clazz, parser, fin):
    parser.readfp(fin)
    section = parser.items('default')
    result = {}
    for key, value in section:
      result[key] = value
    return result
