#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import algorithm, check
from bes.fs import file_util
from bes.debug import debug_timer, noop_debug_timer
from rebuild.base import requirement_manager

from .artifact_manager_base import artifact_manager_base
from .artifact_db import artifact_db
from .artifact_descriptor import artifact_descriptor
from .db_error import *
from .package import package

#log.configure('artifact_manager=debug')

class artifact_manager_chain(artifact_manager_base):

  def __init__(self):
    super(artifact_manager_chain, self).__init__()
    check.check_string(root_dir)
    self._managers = []

  def add_artifact_manager(self, artifact_manager):
    check.check_artifact_manager(artifact_manager)
    self._managers.append(artifact_manager)

  def _find_writable_manager(self):
    can_publish = [ m for m in in self._managers if not m.read_only ]
    if not can_publish:
      raise RuntimeError('No writable artifact manager found.')
    if len(can_publish) > 1:
      raise RuntimeError('Too many writable artifact managers found.')
    return can_publish[0]
    
  #@abstractmethod
  def publish(self, tarball, build_target, allow_replace, metadata):
    m = self._find_writable_manager(self)
    return m.publish(tarball, build_target, allow_replace, metadata)

  #@abstractmethod
  def remove_artifact(self, artifact_descriptor):
    m = self._find_writable_manager(self)
    return m.remove_artifact(artifact_descriptor)
  
  #@abstractmethod
  def list_all_by_descriptor(self, build_target):
    result = []
    for m in self._managers:
      result.extend(m.list_all_by_descriptor(build_target))
    return algorithm.unique(sorted(result))

  #@abstractmethod
  def list_all_by_metadata(self, build_target):
    result = []
    for m in self._managers:
      result.extend(m.list_all_by_metadata(build_target))
    return algorithm.unique(sorted(result))

  #@abstractmethod
  def list_all_by_package_descriptor(self, build_target):
    check.check_build_target(build_target)
    result = []
    for m in self._managers:
      result.extend(m.list_all_by_package_descriptor(build_target))
    return algorithm.unique(sorted(result))
  
  #@abstractmethod
  def find_by_artifact_descriptor(self, artifact_descriptor, relative_filename):
    check.check_artifact_descriptor(artifact_descriptor)
    for m in self._managers:
      try:
        return m.find_by_artifact_descriptor(artifact_descriptor, relative_filename)
      except NotInstalledError as ex:
        pass
    raise NotInstalledError('package \"%s\" not found' % (str(artifact_descriptor)))    
