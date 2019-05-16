#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from rebuild.credentials.credentials_source import credentials_source

from .gradle_properties import gradle_properties

class credentials_source_gradle(credentials_source):

  def __init__(self, filename, name):
    self._filename = filename
    self._name = name
  
  #@abstractmethod
  def is_valid(self):
    if not path.isfile(self._filename):
      return False
    gp = gradle_properties(self._filename)
    return gp.credentials(self._name) is not None

  #@abstractmethod
  def credentials(self):
    gp = gradle_properties(self._filename)
    return gp.credentials(self._name)
