#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# FIXME: add system and machine checking for install_tarball()
# FIXME: theres no notion of transactions or anything else robust in this nice code

import copy, os.path as path

from bes.common import dict_util, json_util, variable
from bes.system import host

from rebuild.pkg_config import pkg_config
from rebuild import build_target, build_type, package_descriptor, System
from bes.fs import dir_util, file_search, file_util, temp_file

from rebuild.package_manager import artifact_manager, ArtifactNotFoundError, Package

class build_requirement_manager(object):

  BUILD_TARGET = build_target(host.SYSTEM, build_type.RELEASE)

  def __init__(self, root_dir):
    self.root_dir = root_dir

  def install_tarball(self, package_tarball):
    package = Package(package_tarball)
    if self.is_installed(package.info):
      return
    package_dir = self.__package_dir(package.info)
    package.extract_files(package_dir)
    replacements = {
      '@REBUILD_PACKAGE_PREFIX@': package_dir,
    }
    file_search.search_replace(package_dir, replacements, backup = False)

  def uninstall(self, package_info):
    if not self.is_installed(package_info):
      return
    package_dir = self.__package_dir(package_info)
    file_util.remove(package_dir)

  def is_installed(self, package_info):
    package_dir = self.__package_dir(package_info)
    return path.isdir(package_dir)

  def __package_dir(self, package_info):
    return path.join(self.root_dir, package_info.full_name)

  def install_package(self, package_info, artifact_manager):
    assert artifact_manager.is_artifact_manager(artifact_manager)
    if self.is_installed(package_info):
      return
    package = artifact_manager.package(package_info, self.BUILD_TARGET)
    self.install_tarball(package.tarball)

  def bin_dir(self, package_info):
    if not self.is_installed(package_info):
      raise RuntimeError('Package not installed: %s' % (package_info))
    return path.join(self.__package_dir(package_info), 'bin')

  def lib_dir(self, package_info):
    if not self.is_installed(package_info):
      raise RuntimeError('Package not installed: %s' % (package_info))
    return path.join(self.__package_dir(package_info), 'lib')

  def env_vars(self, package_info):
    if not self.is_installed(package_info):
      assert False
      return None
    env_vars = copy.deepcopy(package_info.env_vars)
    variables = {
      'REBUILD_PACKAGE_ROOT_DIR': self.__package_dir(package_info),
      'REBUILD_PACKAGE_VERSION': str(package_info.version),
      'REBUILD_PACKAGE_NAME': package_info.name,
    }
    for key, value in env_vars.items():
      env_vars[key] = variable.substitute(value, variables)
    return env_vars

  def python_lib_dir(self, package_info):
    if not self.is_installed(package_info):
      return None
    return path.join(self.__package_dir(package_info), 'lib/python')

  def tool_exe(self, package_info, tool_name):
    if isinstance(package_info, basestring):
      found_package = self.find_package(package_info)
      if not found_package:
        raise RuntimeError('No package found for: %s' % (package_info))
      package_info = found_package
    bin_dir = self.bin_dir(package_info)
    if not bin_dir:
      return None
    exe = path.join(bin_dir, tool_name)
    if not file_util.is_exe(exe):
      return None
    return exe

  def install_packages(self, packages, artifact_manager):
    for package_info in packages:
      self.install_package(package_info, artifact_manager)

  def list_all(self):
    if not path.isdir(self.root_dir):
      return []
    result = []
    package_dirs = dir_util.list(self.root_dir, relative = True)
    for package_dir in package_dirs:
      package_info = package_descriptor.parse(package_dir)
      result.append(package_info)
    return result

  def find_package(self, package_name):
    infos = self.list_all()
    named_packages = [ pi for pi in infos if pi.name == package_name ]
    assert len(named_packages) == 1
    return named_packages[0]

  # FIXME: doesnt deal with multiple versions of tools
  def bin_dirs(self, package_names):
    return [ self.bin_dir(pi) for pi in self.list_all() if pi.name in package_names ]

  # FIXME: doesnt deal with multiple versions of tools
  def python_lib_dirs(self, packages):
    return [ self.python_lib_dir(pi) for pi in packages ]

  # FIXME: doesnt deal with multiple versions of tools
  def all_env_vars(self, packages):
    result = {}
    for pi in packages:
      result.update(self.env_vars(pi))
    return result
