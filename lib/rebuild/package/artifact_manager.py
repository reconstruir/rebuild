#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.system import log
from rebuild.base import build_blurb
from bes.git import git
from bes.fs import dir_util, file_checksum, file_find, file_util
from bes.debug import debug_timer, noop_debug_timer
from rebuild.base import package_descriptor, package_descriptor_list, requirement_manager

from .artifact_db import artifact_db
from .artifact_descriptor import artifact_descriptor
from .db_error import *
from .package import package
from .package_list import package_list

#log.configure('artifact_manager=debug')

class artifact_manager(object):

  DEFAULT_ROOT_DIR = path.expanduser('~/artifacts')

  def __init__(self, root_dir, address = None, no_git = False):
    log.add_logging(self, 'artifact_manager')
    build_blurb.add_blurb(self, 'artifact_manager')

    if root_dir:
      assert string_util.is_string(root_dir)
    
    self._root_dir = path.abspath(root_dir or self.DEFAULT_ROOT_DIR)
    self.no_git = no_git
    
    file_util.mkdir(self._root_dir)
    #self.log_d('Creating instance with root_dir=%s; address=%s' % (self._root_dir, address))
    #self.blurb('Creating instance with root_dir=%s; address=%s' % (self._root_dir, address))

    if not self.no_git:
      if address:
        git.clone_or_pull(address, self._root_dir, enforce_empty_dir = False)
      if not git.is_repo(self._root_dir):
        git.init(self._root_dir)

    self._package_cache = {}
    self._reset()
    self.reload_db()
    self._timer = debug_timer('am', 'error')
#    self._timer = noop_debug_timer('am', 'error')
#    self._sync_db()

    self._db = artifact_db(path.join(self._root_dir, 'artifacts.db'))

  def reload_db(self):
    self._db = artifact_db(path.join(self._root_dir, 'artifacts.db'))
  
  @classmethod
  def _find_possible_artifacts(clazz, root_dir):
    dirs = dir_util.list(root_dir, relative = False)
    dirs = [ d for d in dirs if path.isdir(d) ]
    result = []
    for d in dirs:
      result.extend(file_find.find(d, relative = False))
    return result
                  
  @property
  def root_dir(self):
    return self._root_dir
    
  def _reset(self):
    self._available_packages_map = {}
    self._requirement_managers = {}
    
  def artifact_path(self, package_descriptor, build_target, relative = False):
    filename = '%s.tar.gz' % (package_descriptor.full_name)
    relative_path = path.join(build_target.build_path, filename)
    if relative:
      return relative_path
    return path.join(self._root_dir, relative_path)

  def publish(self, tarball, build_target, allow_replace):
    pkg = package(tarball)
    pkg_info = pkg.package_descriptor
    artifact_path_rel = self.artifact_path(pkg_info, build_target, relative = True)
    artifact_path_abs = self.artifact_path(pkg_info, build_target, relative = False)
    file_util.copy(tarball, artifact_path_abs, use_hard_link = True)
    if not self.no_git:
      git.add(self._root_dir, pkg_info.artifact_path(build_target))
    self._reset()
    pkg_metadata = pkg.metadata.clone_with_filename(artifact_path_rel)
    should_replace = allow_replace and self._db.has_artifact(pkg_metadata.artifact_descriptor)
    if should_replace:
      self._db.replace_artifact(pkg_metadata)
    else:
      self._db.add_artifact(pkg_metadata)
    return artifact_path_abs

  def available_packages(self, build_target):
    if build_target.build_path not in self._available_packages_map:
      self._timer.start('compute available for %s' % (build_target.build_path))
      self._available_packages_map[build_target.build_path] = self._compute_available_packages(build_target)
      self._timer.stop()
    return self._available_packages_map[build_target.build_path]

  def _compute_available_packages(self, build_target):
    d = path.join(self._root_dir, build_target.build_path)
    if not path.exists(d):
      return package_list()
    if not path.isdir(d):
      raise RuntimeError('Not a directory: %s' % (d))
    all_files = dir_util.list(d)
    return package_list([ self._get_package(f) for f in all_files ])
  
  def latest_available_packages(self, build_target):
    return self.available_packages(build_target).latest_versions()

  def resolve_packages(self, package_names, build_target):
    self._timer.start('old resolve_packages()')
    o = self.old_resolve_packages(package_names, build_target)
    self._timer.stop()
    self._timer.start('new resolve_packages()')
    n = self.new_resolve_packages(package_names, build_target)
    self._timer.stop()
    assert len(o) == len(n)
    if False:
#    if True:
      for x, y in zip(o, n):
        print('FOO: OLD: resolved: %s' % (str(x.metadata.package_descriptor.full_name)))
        print('FOO: NEW: resolved: %s' % (str(y.full_name)))
    return o
  
  def old_resolve_packages(self, package_names, build_target):
#    assert False
#    self._timer.start('resolve_packages(package_names %s, build_target %s)' % (package_names, build_target))
    # FIXME: need to deal with multiple versions
    result = []
#    self._timer.start('available_packages(build_target %s)' % (str(build_target)))
    available_packages = self.available_packages(build_target)
#    self._timer.stop()
    for package_name in package_names:
#      self._timer.start('_find_latest_package(package_name %s)' % (package_name))
      available_package = self._find_latest_package(package_name,
                                                     available_packages)
#      self._timer.stop()
      if not available_package:
#        self._timer.stop()
        raise NotInstalledError('package \"%s\" not found' % (package_name))

      result.append(available_package)

    assert len(result) == len(package_names)
#    self._timer.stop()
    return result
  
  def new_resolve_packages(self, package_names, build_target):
#    self._timer.start('resolve_packages(package_names %s, build_target %s)' % (package_names, build_target))
    # FIXME: need to deal with multiple versions
    result = []
#    self._timer.start('available_packages(build_target %s)' % (str(build_target)))
    available_packages = self.list_all_by_metadata(build_target = build_target)
#    self._timer.stop()
    for package_name in package_names:
#      self._timer.start('_find_latest_package(package_name %s)' % (package_name))
      available_package = self._caca_find_latest_package(package_name,
                                                         available_packages)
#      self._timer.stop()
      if not available_package:
#        self._timer.stop()
        raise NotInstalledError('package \"%s\" not found' % (package_name))

      result.append(available_package)

    assert len(result) == len(package_names)
#    self._timer.stop()
    return result
  
  @classmethod
  def _find_latest_package(self, package_name, available_packages):
    candidates = []
    for available_package in available_packages:
      if package_name == available_package.package_descriptor.name:
        candidates.append(available_package)
    if not candidates:
      return None
    if len(candidates) > 1:
      candidates = sorted(candidates, cmp = package.descriptor_cmp)
    return candidates[-1]

  @classmethod
  def _caca_find_latest_package(self, package_name, available_packages):
    check.check_package_metadata_list(available_packages)
    candidates = []
    for available_package in available_packages:
      if package_name == available_package.name:
        candidates.append(available_package)
    if not candidates:
      return None
    if len(candidates) > 1:
      candidates = sorted(candidates, reverse = True) #, cmp = package.descriptor_cmp)
    return candidates[-1]
  
  def list_all_by_descriptor(self, build_target = None):
    return self._db.list_all_by_descriptor(build_target = build_target)

  def list_all_by_metadata(self, build_target = None):
    return self._db.list_all_by_metadata(build_target = build_target)

  def list_latest_versions(self, build_target):
    return self.list_all_by_descriptor(build_target = build_target).latest_versions()
    
  def find_by_package_descriptor(self, package_descriptor, build_target, relative_filename = True):
    check.check_package_descriptor(package_descriptor)
    check.check_build_target(build_target)
    adesc = artifact_descriptor(package_descriptor.name, package_descriptor.version.upstream_version,
                                package_descriptor.version.revision, package_descriptor.version.epoch,
                                build_target.system, build_target.level, build_target.archs, build_target.distro)
    return self.find_by_artifact_descriptor(adesc, relative_filename = relative_filename)

  def find_by_artifact_descriptor(self, artifact_descriptor, relative_filename = True):
    check.check_artifact_descriptor(artifact_descriptor)
    md = self._db.get_artifact(artifact_descriptor)
    if relative_filename:
      return md
    return md.clone_with_filename(path.join(self._root_dir, md.filename))

  def _get_package(self, tarball):
    if not tarball in self._package_cache:
      self._package_cache[tarball] = package(tarball)
    return self._package_cache[tarball]

  def get_requirement_manager(clazz, build_target):
    if not build_target.build_path in self._requirement_managers:
      self._requirement_managers[build_target.build_path] = self._make_requirement_manager(build_target)
    return self._requirement_managers[build_target.build_path]

  def get_requirement_manager(self, build_target):
    if not build_target.build_path in self._requirement_managers:
      self._requirement_managers[build_target.build_path] = self._make_requirement_manager(build_target)
    return self._requirement_managers[build_target.build_path]

  def resolve_deps(self, names, build_target, hardness, include_names):
    return self.get_requirement_manager(build_target).resolve_deps(names, build_target.system, hardness, include_names)
  
  def _make_requirement_manager(self, build_target):
    rm = requirement_manager()
    for package in self.latest_available_packages(build_target):
      rm.add_package(package.package_descriptor)
    return rm

check.register_class(artifact_manager, include_seq = False)
