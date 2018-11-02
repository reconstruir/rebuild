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
    
  #@abstractmethod
  def publish(self, tarball, build_target, allow_replace, metadata):
    raise RuntimeError('artifact_manager_chain is read only.')

  #@abstractmethod
  def remove_artifact(self, adesc):
    raise RuntimeError('artifact_manager_chain is read only.')
  
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
  def find_by_artifact_descriptor(self, adesc, relative_filename):
    check.check_artifact_descriptor(adesc)
    for m in self._managers:
      try:
        return m.find_by_artifact_descriptor(adesc, relative_filename)
      except NotInstalledError as ex:
        pass
    raise NotInstalledError('package \"%s\" not found' % (str(adesc)))    
