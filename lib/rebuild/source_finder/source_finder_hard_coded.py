#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .source_finder import source_finder

class source_finder_hard_coded(source_finder):

  def __init__(self, tarball, name, version):
    self._check_archive_valid(tarball)
    self._tarball = tarball
    self._name = name
    self._version = version
    
  #@abstractmethod
  def find_source(self, name, version, system):
    if name != self._name:
      return None
    if version != self._version:
      return None
    return self._tarball

  #@abstractmethod
  def find_tarball(self, filename):
    return self._tarball

  #@abstractmethod
  def ensure_source(self, filename):
    pass
  
