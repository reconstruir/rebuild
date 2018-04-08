#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.system import log
from rebuild.base import build_blurb
from bes.git import git
from bes.fs import dir_util, file_find, file_util
from rebuild.base import package_descriptor, package_descriptor_list, requirement_manager

from .package import package
from .package_list import package_list
from .db_error import *
from .artifact_db import artifact_db

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
    self._sync_db()

  def _sync_db(self):
    print('finding possible: %s ' % (self._root_dir))
    possible = self._find_possible_artifacts(self._root_dir)
    print('done finding possible')
    for f in possible:
      print('checking %s' % (path.relpath(f)))
      if package.is_package(f):
        print('loading %s' % (path.relpath(f)))
        import sys
        sys.stdout.flush()
        p = package(f)
        print('metadata: %d - %s' % (len(p.metadata.files), str(p.metadata.artifact_descriptor)))
      else:
        print('invalid package: %s' % (f))

  @classmethod
  def _find_possible_artifacts(clazz, root_dir):
    dirs = dir_util.list(root_dir, relative = False)
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
    
  def artifact_path(self, package_descriptor, build_target):
    filename = '%s.tar.gz' % (package_descriptor.full_name)
    return path.join(self._root_dir, build_target.build_path, filename)

  def publish(self, tarball, build_target):
    pkg = package(tarball)
    pkg_info = pkg.package_descriptor
    artifact_path = self.artifact_path(pkg_info, build_target)
    file_util.copy(tarball, artifact_path)
    if not self.no_git:
      git.add(self._root_dir, pkg_info.artifact_path(build_target))
    self._reset()
    return artifact_path

  def available_packages(self, build_target):
    if build_target.build_path not in self._available_packages_map:
      self._available_packages_map[build_target.build_path] = self._compute_available_packages(build_target)
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
    # FIXME: need to deal with multiple versions
    result = []
    available_packages = self.available_packages(build_target)
    for package_name in package_names:
      available_package = self._find_package_by_name(package_name,
                                                     available_packages)
      if not available_package:
        raise NotInstalledError('package \"%s\" not found' % (package_name))

      result.append(available_package)

    assert len(result) == len(package_names)
        
    return result

  def find_package(self, build_target, pkg_desc):
    check.check_build_target(build_target)
    check.check_package_descriptor(pkg_desc)
    for p in self.available_packages(build_target):
      if pkg_desc.name == p.package_descriptor.name and pkg_desc.version == p.package_descriptor.version:
        return p
    return None
  
  @classmethod
  def _find_package_by_name(self, package_name, available_packages):
    candidates = []
    for available_package in available_packages:
      if package_name == available_package.package_descriptor.name:
        candidates.append(available_package)
    if not candidates:
      return None
    if len(candidates) > 1:
      candidates = sorted(candidates, cmp = package.descriptor_cmp)
    return candidates[-1]

  def package(self, package_descriptor, build_target):
    tarball = self.artifact_path(package_descriptor, build_target)
    if not path.isfile(tarball):
      raise NotInstalledError('Artifact \"%s\" not found for %s' % (tarball, package_descriptor.full_name),
                              package_descriptor)
    return self._get_package(tarball)

  def _get_package(self, tarball):
    if not tarball in self._package_cache:
      self._package_cache[tarball] = package(tarball)
    return self._package_cache[tarball]

#  def dependency_map(self, build_target):
#    available = self.available_packages(build_target).descriptors()
#    return package_descriptor_list.dependency_map(available)

  def get_requirement_manager(clazz, build_target):
    if not build_target.build_path in self._requirement_managers:
      self._requirement_managers[build_target.build_path] = self._make_requirement_manager(build_target)
    return self._requirement_managers[build_target.build_path]

  def get_requirement_manager(self, build_target):
    if not build_target.build_path in self._requirement_managers:
      self._requirement_managers[build_target.build_path] = self._make_requirement_manager(build_target)
    return self._requirement_managers[build_target.build_path]

  def resolve(self, names, build_target):
    return self.get_requirement_manager(build_target).resolve(names, build_target.system)
  
  def resolve_deps(self, names, build_target):
    return self.get_requirement_manager(build_target).resolve_deps(names, build_target.system)

  def resolve_deps_poto(self, names, build_target, hardness, include_names):
    return self.get_requirement_manager(build_target).resolve_deps_poto(names, build_target.system, hardness, include_names)
  
  def _make_requirement_manager(self, build_target):
    rm = requirement_manager()
    for package in self.latest_available_packages(build_target):
      rm.add_package(package.package_descriptor)
    return rm
  
check.register_class(artifact_manager, include_seq = False)
