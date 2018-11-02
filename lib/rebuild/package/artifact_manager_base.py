#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common import check

class artifact_manager_base(with_metaclass(ABCMeta, object)):

  @abstractmethod
  def reload_db(self):
    pass
  
  @abstractmethod
  def artifact_path(self, package_descriptor, build_target, relative):
    pass
  
  @abstractmethod
  def publish(self, tarball, build_target, allow_replace, metadata):
    pass
    
  @abstractmethod
  def remove_artifact(self, adesc):
    pass
  
  @abstractmethod
  def latest_packages(self, package_names, build_target):
    pass
  
  @abstractmethod
  def list_all_by_descriptor(self, build_target = None):
    pass

  @abstractmethod
  def list_all_by_metadata(self, build_target = None):
    pass

  @abstractmethod
  def list_all_by_package_descriptor(self, build_target = None):
    pass

  @abstractmethod
  def list_latest_versions(self, build_target):
    pass
    
  @abstractmethod
  def find_by_package_descriptor(self, package_descriptor, build_target, relative_filename):
    pass

  @abstractmethod
  def find_by_artifact_descriptor(self, adesc, relative_filename):
    pass

  @abstractmethod
  def get_requirement_manager(clazz, build_target):
    pass

  @abstractmethod
  def resolve_deps(self, names, build_target, hardness, include_names):
    pass

check.register_class(artifact_manager_base, name = 'artifact_manager', include_seq = False)
