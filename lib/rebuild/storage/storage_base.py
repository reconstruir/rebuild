#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from collections import namedtuple

from .storage_registry import storage_registry

class storage_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    storage_registry.register(clazz)
    return clazz

class storage_base(with_metaclass(storage_register_meta, object)):

  @abstractmethod
  def reload_available(self):
    pass
  
  @abstractmethod
  def find_tarball(self, filename):
    pass

  @abstractmethod
  def ensure_source(self, filename):
    pass

  @abstractmethod
  def search(self, name):
    pass

  @abstractmethod
  def upload(self, local_filename, remote_filename, local_checksum):
    pass

  @abstractmethod
  def remote_checksum(self, remote_filename):
    pass

  @abstractmethod
  def remote_filename_abs(self, remote_filename):
    pass

  _entry = namedtuple('_entry', 'filename, sha1_checksum')
  @abstractmethod
  def list_all_files(self):
    'Return a list of filename, sha1_checksum entries.'
    pass
