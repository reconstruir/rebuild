#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.system import log
from rebuild.base import build_blurb
from bes.git import git
from bes.fs import file_util
from bes.debug import debug_timer, noop_debug_timer
from rebuild.base import requirement_manager

from .artifact_db import artifact_db
from .artifact_descriptor import artifact_descriptor
from .db_error import *
from .package import package

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
  
  @property
  def root_dir(self):
    return self._root_dir
    
  def _reset(self):
    self._requirement_managers = {}
    
  def artifact_path(self, package_descriptor, build_target, relative = False):
    filename = '%s.tar.gz' % (package_descriptor.full_name)
    relative_path = path.join(build_target.build_path, filename)
    if relative:
      return relative_path
    return path.join(self._root_dir, relative_path)

  def publish(self, tarball, build_target, allow_replace, metadata = None):
    if not metadata:
      metadata = package(tarball).metadata
    check.check_package_metadata(metadata)
    pkg_desc = metadata.package_descriptor
    artifact_path_rel = self.artifact_path(pkg_desc, build_target, relative = True)
    artifact_path_abs = self.artifact_path(pkg_desc, build_target, relative = False)
    file_util.copy(tarball, artifact_path_abs, use_hard_link = True)
    if not self.no_git:
      git.add(self._root_dir, pkg_desc.artifact_path(build_target))
    self._reset()
    pkg_metadata = metadata.clone_with_filename(artifact_path_rel)
    should_replace = allow_replace and self._db.has_artifact(pkg_metadata.artifact_descriptor)
    if should_replace:
      self._db.replace_artifact(pkg_metadata)
    else:
      self._db.add_artifact(pkg_metadata)
    return artifact_path_abs

  def latest_packages(self, package_names, build_target):
    result = []
    available_packages = self.list_all_by_metadata(build_target = build_target)
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
  
  def list_all_by_descriptor(self, build_target = None):
    return self._db.list_all_by_descriptor(build_target = build_target)

  def list_all_by_metadata(self, build_target = None):
    return self._db.list_all_by_metadata(build_target = build_target)

  def list_all_by_package_descriptor(self, build_target = None):
    return self._db.list_all_by_package_descriptor(build_target = build_target)

  def list_latest_versions(self, build_target):
    return self.list_all_by_descriptor(build_target = build_target).latest_versions()
    
  def find_by_package_descriptor(self, package_descriptor, build_target, relative_filename = True):
    check.check_package_descriptor(package_descriptor)
    check.check_build_target(build_target)
    adesc = artifact_descriptor(package_descriptor.name, package_descriptor.version.upstream_version,
                                package_descriptor.version.revision, package_descriptor.version.epoch,
                                build_target.system, build_target.level, build_target.arch,
                                build_target.distro, build_target.distro_version)
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
    self._timer.start('_make_requirement_manager() for %s' % (str(build_target)))
    rm = requirement_manager()
    latest_versions = self.list_all_by_package_descriptor(build_target = build_target).latest_versions()
    for pkg_desc in latest_versions:
      rm.add_package(pkg_desc)
    self._timer.stop()
    return rm

check.register_class(artifact_manager, include_seq = False)
