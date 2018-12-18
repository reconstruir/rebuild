#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common import check
from bes.system import log
from bes.debug import debug_timer

from rebuild.base import artifact_descriptor, build_blurb, requirement_manager

from .db_error import *

class artifact_manager_base(with_metaclass(ABCMeta, object)):

  def __init__(self):
    log.add_logging(self, 'artifact_manager')
    build_blurb.add_blurb(self, 'artifact_manager')
    self._reset_requirement_managers()
    self._read_only = False
    self._timer = debug_timer('am', 'error', disabled = True)
    
  @property
  def read_only(self):
    return self._read_only

  @read_only.setter
  def read_only(self, value):
    self._read_only = value

  @abstractmethod
  def artifact_path(self, package_descriptor, build_target, relative):
    pass
    
  @abstractmethod
  def publish(self, tarball, build_target, allow_replace, metadata):
    pass
    
  @abstractmethod
  def remove_artifact(self, artifact_descriptor):
    pass
  
  @abstractmethod
  def list_all_by_descriptor(self, build_target):
    pass

  @abstractmethod
  def list_all_by_metadata(self, build_target):
    pass

  @abstractmethod
  def list_all_by_package_descriptor(self, build_target):
    pass

  @abstractmethod
  def find_by_artifact_descriptor(self, artifact_descriptor, relative_filename):
    pass

  @abstractmethod
  def download(self, adesc):
    pass
  
  @abstractmethod
  def needs_download(self, adesc):
    pass
  
  def find_by_package_descriptor(self, pdesc, build_target, relative_filename):
    check.check_package_descriptor(pdesc)
    check.check_build_target(build_target)
    self.log_i('by_package_descriptor(pdesc=%s, build_target=%s, relative_filename=%s)' % (str(pdesc),
                                                                                           build_target.build_path,
                                                                                           relative_filename))
    adesc = artifact_descriptor(pdesc.name, pdesc.version.upstream_version,
                                pdesc.version.revision, pdesc.version.epoch,
                                build_target.system, build_target.level, build_target.arch,
                                build_target.distro, build_target.distro_version)
    return self.find_by_artifact_descriptor(adesc, relative_filename)
 
  def has_package_by_descriptor(self, pdesc, build_target):
    try:
      self.find_by_package_descriptor(pdesc, build_target, False)
      return True
    except NotInstalledError as ex:
      pass
    return False
 
  def latest_packages(self, package_names, build_target):
    self.log_i('latest_packages(package_names=%s, build_target=%s)' % (' '.join(package_names),
                                                                       build_target.build_path))
    result = []
    available_packages = self.list_all_by_metadata(build_target)
    for available_package in available_packages:
      self.log_d('latest_packages: AVAILABLE: %s' % (str(available_package.artifact_descriptor)))
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
      candidates = sorted(candidates, key = lambda candidate: candidate.build_version)
    for candidate in candidates:
      self.log_d('_find_latest_package: CANDIDATE for %s: %s' % (package_name, candidate.artifact_descriptor))
    return candidates[-1]
  
  def _reset_requirement_managers(self):
    self._requirement_managers = {}

  def _make_requirement_manager(self, build_target):
    self.log_i('_make_requirement_manager(build_target=%s)' % (build_target.build_path))
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
    self.log_i('resolve_deps(names=%s, build_target=%s, hardness=%s, include_names=%s)' % (' '.join(names),
                                                                                           build_target.build_path,
                                                                                           ' '.join(hardness),
                                                                                           include_names))
    rm = self.get_requirement_manager(build_target)
    self.log_i('resolve_deps() requirements_manager dep_map=%s' % (rm.descriptor_map_to_string()))
    return rm.resolve_deps(names, build_target.system, hardness, include_names)

  def list_latest_versions(self, build_target):
    return self.list_all_by_descriptor(build_target).latest_versions()
  
check.register_class(artifact_manager_base, name = 'artifact_manager', include_seq = False)
