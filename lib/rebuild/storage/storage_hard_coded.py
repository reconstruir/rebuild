#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.archive.archiver import archiver

from .storage_base import storage_base 

class storage_hard_coded(storage_base):

  def __init__(self, tarball):
    if not archiver.is_valid(tarball):
      raise RuntimeError('Invalid archive: %s' % (tarball))
    self._tarball = tarball

  #@abstractmethod
  def reload_available(self):
    pass
    
  #@abstractmethod
  def find_tarball(self, filename):
    return self._tarball

  #@abstractmethod
  def ensure_source(self, filename):
    assert False
  
  #@abstractmethod
  def search(self, name):
    assert False

  #@abstractmethod
  def upload(self, local_filename, remote_filename, local_checksum):
    assert False

  #@abstractmethod
  def set_properties(self, filename, properties):
    assert False
    
  #@abstractmethod
  def remote_checksum(self, remote_filename):
    assert False

  #@abstractmethod
  def list_all_files(self):
    assert False
