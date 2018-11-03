#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check
from rebuild.base import package_descriptor_list

from .artifact_manager_base import artifact_manager_base
from .db_error import *

from .artifact_descriptor_list import artifact_descriptor_list
from .package_metadata_list import package_metadata_list

class artifact_manager_chain(artifact_manager_base):

  def __init__(self):
    super(artifact_manager_chain, self).__init__()
    self._managers = []

  def add_artifact_manager(self, artifact_manager):
    check.check_artifact_manager(artifact_manager)
    self._managers.append(artifact_manager)
    self._reset_requirement_managers()

  def _find_writable_manager(self):
    can_publish = [ m for m in self._managers if not m.read_only ]
    if not can_publish:
      raise RuntimeError('No writable artifact manager found.')
    if len(can_publish) > 1:
      raise RuntimeError('Too many writable artifact managers found.')
    return can_publish[0]

  #@abstractmethod
  def artifact_path(self, package_descriptor, build_target, relative):
    for m in self._managers:
      p = m.artifact_path(package_descriptor, build_target, relative)
      if p:
        return p
    return None
  
  #@abstractmethod
  def publish(self, tarball, build_target, allow_replace, metadata):
    m = self._find_writable_manager()
    result =  m.publish(tarball, build_target, allow_replace, metadata)
    self._reset_requirement_managers()
    return result

  #@abstractmethod
  def remove_artifact(self, artifact_descriptor):
    m = self._find_writable_manager(self)
    return m.remove_artifact(artifact_descriptor)
  
  #@abstractmethod
  def list_all_by_descriptor(self, build_target):
    result = artifact_descriptor_list()
    for m in self._managers:
      result.extend(m.list_all_by_descriptor(build_target))
    result.remove_dups()
    return result

  #@abstractmethod
  def list_all_by_metadata(self, build_target):
    result = package_metadata_list()
    for m in self._managers:
      result.extend(m.list_all_by_metadata(build_target))
    result.remove_dups()
    return result

  #@abstractmethod
  def list_all_by_package_descriptor(self, build_target):
    check.check_build_target(build_target)
    result = package_descriptor_list()
    for m in self._managers:
      result.extend(m.list_all_by_package_descriptor(build_target))
    result.remove_dups()
    return result
  
  #@abstractmethod
  def find_by_artifact_descriptor(self, artifact_descriptor, relative_filename):
    check.check_artifact_descriptor(artifact_descriptor)
    for m in self._managers:
      try:
        return m.find_by_artifact_descriptor(artifact_descriptor, relative_filename)
      except NotInstalledError as ex:
        pass
    raise NotInstalledError('package \"%s\" not found' % (str(artifact_descriptor)), artifact_descriptor)
