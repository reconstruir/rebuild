#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from abc import abstractmethod, ABCMeta
from bes.system.compat import with_metaclass
from bes.common import check
from bes.system import log
from bes.debug import debug_timer

from rebuild.base import artifact_descriptor, build_blurb, package_descriptor_list, requirement_manager

from .db_error import *
from .artifact_manager_registry import artifact_manager_registry

class artifact_manager_register_meta(ABCMeta):
  
  def __new__(meta, name, bases, class_dict):
    clazz = ABCMeta.__new__(meta, name, bases, class_dict)
    artifact_manager_registry.register(clazz)
    return clazz

class artifact_manager_base(with_metaclass(artifact_manager_register_meta, object)):

  def __init__(self):
    log.add_logging(self, 'am')
    build_blurb.add_blurb(self, 'rebuild')
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
  def publish(self, tarball, allow_replace, metadata):
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

  def _log_label(self, method):
    return '%s(%s): %s:' % (self.__class__.__name__, id(self), method)
  
  def find_by_package_descriptor(self, pdesc, build_target, relative_filename):
    check.check_package_descriptor(pdesc)
    check.check_build_target(build_target)
    self.log_d('%s: pdesc=%s; build_target=%s; relative_filename=%s' % (self._log_label('find_by_package_descriptor'),
                                                                        str(pdesc),
                                                                        build_target.build_path,
                                                                        relative_filename))
    adesc = artifact_descriptor.make_from_package_descriptor(pdesc, build_target)
    adesc_no_distro = adesc.clone_without_distro()
    try:
      return self.find_by_artifact_descriptor(adesc_no_distro, relative_filename)
    except NotInstalledError as ex:
      pass
    return self.find_by_artifact_descriptor(adesc, relative_filename)
 
  def has_package_by_descriptor(self, pdesc, build_target):
    try:
      self.find_by_package_descriptor(pdesc, build_target, False)
      return True
    except NotInstalledError as ex:
      pass
    return False
 
  def packages_dict(self, build_target):
    all_packages = self.list_all_by_package_descriptor(build_target)
    result = {}
    for pd in all_packages:
      if pd.name not in result:
        result[pd.name] = package_descriptor_list()
      result[pd.name].append(pd)
    return result

  def list_all_filter_with_requirements(self, build_target, requirements):
    pdict = self.packages_dict(build_target)
    rdict = requirements.to_dict()
    result = package_descriptor_list()
    for name in sorted(pdict.keys()):
      packages = pdict[name]
      if name in rdict:
        req = rdict[name]
        packages = packages.filter_by_requirement(req)
      result.extend(packages)
    return result
  
  def _reset_requirement_managers(self):
    self.log_d('%s' % (self._log_label('_reset_requirement_managers')))
    self._requirement_managers = {}

  def _make_requirement_manager(self, build_target):
    self.log_d('%s build_target=%s' % (self._log_label('_make_requirement_manager'), build_target.build_path))
    self._timer.start('_make_requirement_manager() for %s' % (str(build_target)))
    rm = requirement_manager()
    latest_versions = self.list_all_by_package_descriptor(build_target).latest_versions()
    self.log_d('%s: latest_versions=%s' % (self._log_label('_make_requirement_manager'), str(latest_versions)))
    for pkg_desc in latest_versions:
      rm.add_package(pkg_desc)
    self._timer.stop()
    return rm
    
  def get_requirement_manager(self, build_target):
    if not build_target.build_path in self._requirement_managers:
      self._requirement_managers[build_target.build_path] = self._make_requirement_manager(build_target)
    return self._requirement_managers[build_target.build_path]

  def resolve_deps(self, names, build_target, hardness, include_names):
    check.check_string_seq(names)
    check.check_build_target(build_target)
    check.check_string_seq(hardness)
    check.check_bool(include_names)
    self.log_d('%s: names=%s; build_target=%s; hardness=%s; include_names=%s' % (self._log_label('resolve_deps'),
                                                                                       ' '.join(names),
                                                                                       build_target.build_path,
                                                                                       ' '.join(hardness),
                                                                                       include_names))
    rm = self.get_requirement_manager(build_target)
    self.log_d('%s: build_target=%s; dep_map=%s' % (self._log_label('resolve_deps'), build_target, rm.descriptor_map_to_string()))
    return rm.resolve_deps(names, build_target.system, hardness, include_names)

  def list_latest_versions(self, build_target):
    return self.list_all_by_descriptor(build_target).latest_versions()

  _poto_resolve_result = namedtuple('_poto_resolve_result', 'available, latest, resolved, missing')
  def poto_resolve_deps(self, requirements, build_target, hardness, include_names):
    check.check_requirement_list(requirements)
    check.check_build_target(build_target)
    check.check_string_seq(hardness)
    check.check_bool(include_names)
    self.log_d('%s: build_target=%s; requirements=%s; hardness=%s; include_names=%s' % (self._log_label('poto_resolve_deps'),
                                                                                        build_target.build_path,
                                                                                        requirements,
                                                                                        ' '.join(hardness),
                                                                                        include_names))
    rm = requirement_manager()
    available = self.list_all_filter_with_requirements(build_target, requirements)
    latest = available.latest_versions()
    rm.add_packages(latest)
    rm_rv = rm.resolve_deps_NEW(requirements.names(), build_target.system, hardness, include_names)
    if rm_rv.missing:
      result = self._poto_resolve_result(available, latest, None, rm_rv.missing)
    else:
      result = self._poto_resolve_result(available, latest, rm_rv.resolved, None)
    return result

  def import_artifact(self, other_am, pkg_desc, build_target, checksum_getter):
    check.check_artifact_manager(other_am)
    check.check_package_descriptor(pkg_desc)
    check.check_build_target(build_target)
    check.check_file_checksum_getter(checksum_getter)
    self.log_d('%s: other_am=%s; pkg_desc=%s; build_target=%s' % (self._log_label('import_artifact'),
                                                                  other_am,
                                                                  pkg_desc,
                                                                  build_target))
    adesc = artifact_descriptor.make_from_package_descriptor(pkg_desc, build_target)
    if not other_am.has_package_by_descriptor(pkg_desc, build_target):
      raise RuntimeError('Artifact \"%s\" not found in %s' % (adesc, other_am))
    other_am.download(adesc)
    old_tarball = self.artifact_path(pkg_desc, build_target, False)
    old_checksum = checksum_getter.checksum('sha256', old_tarball) if old_tarball else None
    new_tarball = other_am.artifact_path(pkg_desc, build_target, False)
    assert path.isfile(new_tarball)
    new_checksum = checksum_getter.checksum('sha256', new_tarball)
    if old_checksum != new_checksum:
      md = other_am.find_by_artifact_descriptor(adesc, False)
      self.log_d('%s: importing %s from %s to %s' % (self._log_label('import_artifact'), adesc, other_am, self))
      self.blurb('imported %s from %s' % (str(adesc), str(other_am)))
      self.publish(new_tarball, True, md)
  
check.register_class(artifact_manager_base, name = 'artifact_manager', include_seq = False)
