#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# FIXME: add system and machine checking for install_tarball()
# FIXME: theres no notion of transactions or anything else robust in this nice code

import copy, os.path as path

from bes.common import dict_util, json_util, string_util, variable
from bes.system import host

from rebuild.pkg_config import pkg_config
from rebuild.base import build_target, build_system, build_level, package_descriptor
from bes.fs import dir_util, file_search, file_util, file_path, temp_file

from rebuild.package_manager import artifact_manager, ArtifactNotFoundError, package

class build_requirement_manager(object):

  BUILD_TARGET = build_target(host.SYSTEM, build_level.RELEASE)

  def __init__(self, root_dir):
    self.root_dir = root_dir

  def install_tarball(self, package_tarball):
    pkg = package(package_tarball)
    if self.is_installed(pkg.info):
      return
    pkg_dir = self.__package_dir(pkg.info)
    pkg.extract_files(pkg_dir)
    replacements = {
      '@REBUILD_PACKAGE_PREFIX@': pkg_dir,
    }
    file_search.search_replace(pkg_dir, replacements, backup = False)

  def uninstall(self, pkg_desc):
    if not self.is_installed(pkg_desc):
      return
    pkg_dir = self.__package_dir(pkg_desc)
    file_util.remove(pkg_dir)

  def is_installed(self, pkg_desc):
    pkg_dir = self.__package_dir(pkg_desc)
    return path.isdir(pkg_dir)

  def __package_dir(self, pkg_desc):
    return path.join(self.root_dir, pkg_desc.full_name)

  def install_package(self, pkg_desc, artifact_manager):
    assert artifact_manager.is_artifact_manager(artifact_manager)
    if self.is_installed(pkg_desc):
      return
    package = artifact_manager.package(pkg_desc, self.BUILD_TARGET)
    self.install_tarball(package.tarball)

  def bin_dir(self, pkg_desc):
    if not self.is_installed(pkg_desc):
      raise RuntimeError('package not installed: %s' % (pkg_desc))
    return path.join(self.__package_dir(pkg_desc), 'bin')

  def lib_dir(self, pkg_desc):
    if not self.is_installed(pkg_desc):
      raise RuntimeError('package not installed: %s' % (pkg_desc))
    return path.join(self.__package_dir(pkg_desc), 'lib')

  def env_vars(self, pkg_desc):
    if not self.is_installed(pkg_desc):
      assert False
      return None
    env_vars = copy.deepcopy(pkg_desc.env_vars)
    variables = {
      'REBUILD_PACKAGE_ROOT_DIR': self.__package_dir(pkg_desc),
      'REBUILD_PACKAGE_VERSION': str(pkg_desc.version),
      'REBUILD_PACKAGE_NAME': pkg_desc.name,
    }
    for key, value in env_vars.items():
      env_vars[key] = variable.substitute(value, variables)
    return env_vars

  def python_lib_dir(self, pkg_desc):
    if not self.is_installed(pkg_desc):
      return None
    return path.join(self.__package_dir(pkg_desc), 'lib/python')

  def tool_exe(self, pkg_desc, tool_name):
    if string_util.is_string(pkg_desc):
      found_package = self.find_package(pkg_desc)
      if not found_package:
        raise RuntimeError('No package found for: %s' % (pkg_desc))
      pkg_desc = found_package
    bin_dir = self.bin_dir(pkg_desc)
    if not bin_dir:
      return None
    exe = path.join(bin_dir, tool_name)
    if not file_path.is_executable(exe):
      return None
    return exe

  def install_packages(self, packages, artifact_manager):
    for pkg_desc in packages:
      self.install_package(pkg_desc, artifact_manager)

  def list_all(self):
    if not path.isdir(self.root_dir):
      return []
    result = []
    package_dirs = dir_util.list(self.root_dir, relative = True)
    for package_dir in package_dirs:
      pkg_desc = package_descriptor.parse(package_dir)
      result.append(pkg_desc)
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
