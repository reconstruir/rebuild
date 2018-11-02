#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common import check
from bes.system import log

from rebuild.base import build_blurb, requirement_manager

from .artifact_descriptor import artifact_descriptor

class artifact_manager_base(with_metaclass(ABCMeta, object)):

  def __init__(self):
    log.add_logging(self, 'artifact_manager')
    build_blurb.add_blurb(self, 'artifact_manager')
    self._reset_requirement_managers()
    self._read_only = False
    
  @property
  def read_only(self):
    return self._read_only

  @read_only.setter
  def read_only(self, value):
    self._read_only = value
    
  @abstractmethod
  def publish(self, tarball, build_target, allow_replace, metadata):
    pass
    
  @abstractmethod
  def remove_artifact(self, artifact_descriptor):
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
  def find_by_artifact_descriptor(self, artifact_descriptor, relative_filename):
    pass

  def find_by_package_descriptor(self, package_descriptor, build_target, relative_filename):
    check.check_package_descriptor(package_descriptor)
    check.check_build_target(build_target)
    artifact_descriptor = artifact_descriptor(package_descriptor.name, package_descriptor.version.upstream_version,
                                package_descriptor.version.revision, package_descriptor.version.epoch,
                                build_target.system, build_target.level, build_target.arch,
                                build_target.distro, build_target.distro_version)
    return self.find_by_artifact_descriptor(artifact_descriptor, relative_filename)
 
 
  def latest_packages(self, package_names, build_target):
    result = []
    available_packages = self.list_all_by_metadata(build_target)
    for package_name in package_names:
      available_package = self._find_latest_package(package_name, available_packages)
      if not available_package:
        raise NotInstalledError('package \"%s\" not found' % (package_name))
      result.append(available_package)
    assert len(result) == len(package_names)
    return result
  
  @classmethod
  def _find_latest_package(self, package_name, available_packages):
    check.check_package_metadata_list(available_packages)
    candidates = [ p for p in available_packages if p.name == package_name ]
    if not candidates:
      return None
    if len(candidates) > 1:
      candidates = sorted(candidates, reverse = True)
    return candidates[-1]
  
  def artifact_path(self, package_descriptor, build_target, relative):
    check.check_package_descriptor(package_descriptor)
    check.check_build_target(build_target)
    filename = '%s.tar.gz' % (package_descriptor.full_name)
    relative_path = path.join(build_target.build_path, filename)
    if relative:
      return relative_path
    return path.join(self._root_dir, relative_path)

  def _reset_requirement_managers(self):
    self._requirement_managers = {}

  def _make_requirement_manager(self, build_target):
    self._timer.start('_make_requirement_manager() for %s' % (str(build_target)))
    rm = requirement_manager()
    latest_versions = self.list_all_by_package_descriptor(build_target).latest_versions()
    for pkg_desc in latest_versions:
      rm.add_package(pkg_desc)
    self._timer.stop()
    return rm
    
  def get_requirement_manager(self, build_target):
    if not build_target.build_path in self._requirement_managers:
      self._requirement_managers[build_target.build_path] = self._make_requirement_manager(build_target)
    return self._requirement_managers[build_target.build_path]

  def resolve_deps(self, names, build_target, hardness, include_names):
    return self.get_requirement_manager(build_target).resolve_deps(names, build_target.system, hardness, include_names)

  def list_latest_versions(self, build_target):
    return self.list_all_by_descriptor(build_target).latest_versions()
  
check.register_class(artifact_manager_base, name = 'artifact_manager', include_seq = False)
