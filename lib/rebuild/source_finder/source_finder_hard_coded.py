#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.archive import archiver

from .source_finder import source_finder

class source_finder_hard_coded(source_finder):

  def __init__(self, tarball):
    if not archiver.is_valid(tarball):
      raise RuntimeError('Invalid archive: %s' % (tarball))
    self._tarball = tarball
    
  #@abstractmethod
  def find_tarball(self, filename):
    return self._tarball

  #@abstractmethod
  def ensure_source(self, filename):
    pass
  
