#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import string_util
from bes.system import log
from rebuild import build_blurb, package_descriptor, package_descriptor_list
from bes.git import git
from bes.fs import dir_util, file_util

from .Package import Package
from .package_list import package_list

class ArtifactNotFoundError(Exception):
  pass

#log.configure('artifact_manager=debug')

class artifact_manager(object):

  DEFAULT_PUBLISH_DIR = path.expanduser('~/artifacts')

  def __init__(self, publish_dir, address = None, no_git = False):
    log.add_logging(self, 'artifact_manager')
    build_blurb.add_blurb(self, 'artifact_manager')

    if publish_dir:
      assert string_util.is_string(publish_dir)
    
    self.publish_dir = path.abspath(publish_dir or self.DEFAULT_PUBLISH_DIR)
    self.no_git = no_git
    
    file_util.mkdir(self.publish_dir)
    #self.log_d('Creating instance with publish_dir=%s; address=%s' % (self.publish_dir, address))
    #self.blurb('Creating instance with publish_dir=%s; address=%s' % (self.publish_dir, address))

    if not self.no_git:
      if address:
        git.clone_or_update(address, self.publish_dir, enforce_empty_dir = False)
      if not git.is_repo(self.publish_dir):
        git.init(self.publish_dir)

    self._package_cache = {}

  def artifact_path(self, package_info, build_target):
    filename = '%s.tar.gz' % (package_info.full_name)
    return path.join(self.publish_dir, build_target.build_name, filename)

  def publish(self, tarball, build_target):
    package = Package(tarball)
    package_info = package.info
    artifact_path = self.artifact_path(package_info, build_target)
    file_util.copy(tarball, artifact_path)
    if not self.no_git:
      git.add(self.publish_dir, package_info.artifact_path(build_target))
    return artifact_path

  def available_packages(self, build_target):
    d = path.join(self.publish_dir, build_target.system, build_target.build_type)
    if not path.exists(d):
      return []
    if not path.isdir(d):
      raise RuntimeError('Not a directory: %s' % (d))
    all_files = dir_util.list(d)
    return [ self.__load_package(f) for f in all_files ]

  def latest_available_packages(self, build_target):
    available = self.available_packages(build_target)
    return package_list.latest_versions(available)

  def resolve_packages(self, package_names, build_target):
    # FIXME: need to deal with multiple versions
    result = []
    available_packages = self.available_packages(build_target)
    for package_name in package_names:
      available_package = self.__find_package_by_name(package_name,
                                                      available_packages)
      if not available_package:
        raise ArtifactNotFoundError('Package \"%s\" not found' % (package_name))

      result.append(available_package)

    assert len(result) == len(package_names)
        
    return result

  @classmethod
  def __find_package_by_name(self, package_name, available_packages):
    candidates = []
    for available_package in available_packages:
      if package_name == available_package.info.name:
        candidates.append(available_package)
    if not candidates:
      return None
    if len(candidates) > 1:
      candidates = sorted(candidates, cmp = Package.info_cmp)
    return candidates[-1]

  @classmethod
  def is_artifact_manager(clazz, o):
    return isinstance(o, artifact_manager)

  def package(self, package_info, build_target):
    tarball = self.artifact_path(package_info, build_target)
    if not path.isfile(tarball):
      raise ArtifactNotFoundError('Artifact \"%s\" not found for %s' % (tarball, package_info.full_name))
    return self.__load_package(tarball)

#  @classmethod
#  def parse_filename(clazz, filename):
#    s = string_util.remove_tail(filename, '.tar.gz')
#    return package_descriptor.parse(s)

  def __load_package(self, tarball):
    if not tarball in self._package_cache:
      self._package_cache[tarball] = Package(tarball)
    return self._package_cache[tarball]

  def dependency_map(self, build_target):
    available = package_list.descriptors(self.available_packages(build_target))
    return package_descriptor_list.dependency_map(available)
