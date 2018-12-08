#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
#from bes.common import check
#from rebuild.base import build_system
#from .tarball_finder import tarball_finder
from .storage_registry import storage_registry

class storage_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    storage_registry.register(clazz)
    return clazz

class storage_base(with_metaclass(storage_register_meta, object)):

  @abstractmethod
  def find_tarball(self, filename):
    pass

  @abstractmethod
  def ensure_source(self, filename):
    pass

  @abstractmethod
  def search(self, name):
    pass

#  @classmethod
#  def _find_by_filename(self, where, filename):
#    return tarball_finder.find_by_filename(where, filename)
