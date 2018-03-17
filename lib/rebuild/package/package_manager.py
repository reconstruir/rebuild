#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# FIXME: theres no notion of transactions or anything else robust in this nice code

import copy, os.path as path, platform
from bes.common import check, object_util, string_util, variable
from bes.system import os_env, os_env_var
from rebuild.instruction import instruction_list
from rebuild.base import build_system, requirement
from bes.dependency import dependency_resolver
from rebuild.pkg_config import pkg_config
from bes.archive import archive, archiver
from bes.fs import file_util
from .artifact_manager import artifact_manager, ArtifactNotFoundError
from .package import package
from .package_db import package_db
from rebuild.base import package_descriptor, package_descriptor_list
from .package_list import package_list

class PackageFilesConflictError(Exception):
  def __init__(self, message):
    super(PackageFilesConflictError, self).__init__()
    self.message = message

  def __str__(self):
    return self.message
  
class PackageNotFoundError(Exception):
  def __init__(self, message):
    super(PackageNotFoundError, self).__init__()
    self.message = message

  def __str__(self):
    return self.message
  
class PackageAlreadyInstallededError(Exception):
  def __init__(self, message):
    super(PackageAlreadyInstallededError, self).__init__()
    self.message = message

  def __str__(self):
    return self.message
  
class PackageMissingRequirementsError(Exception):
  def __init__(self, message):
    super(PackageMissingRequirementsError, self).__init__()
    self.message = message

  def __str__(self):
    return self.message
  
class package_manager(object):

  def __init__(self, root_dir):
    self.root_dir = root_dir
    self._database_path = path.join(self.root_dir, 'database/packages.json')
    self._db = package_db(self._database_path)
    self._installation_dir = path.join(self.root_dir, 'installation')
    self._env_dir = path.join(self.root_dir, 'env')
    self._lib_dir = path.join(self._installation_dir, 'lib')
    self._bin_dir = path.join(self._installation_dir, 'bin')
    self._include_dir = path.join(self._installation_dir, 'include')
    self._python_lib_dir = path.join(self._installation_dir, 'lib/python')
    self._share_dir = path.join(self._installation_dir, 'share')
    self._compile_instructions_dir = path.join(self._installation_dir, 'lib/rebuild_instructions')

  @property
  def installation_dir(self): 
    return self._installation_dir

  @property
  def env_dir(self):
    return self._env_dir

  @property
  def lib_dir(self):
    return self._lib_dir

  @property
  def python_lib_dir(self):
    return self._python_lib_dir

  @property
  def bin_dir(self):
    return self._bin_dir

  @property
  def include_dir(self):
    return self._include_dir

  @property
  def share_dir(self):
    return self._share_dir

  @property
  def pkg_config_path(self):
    return pkg_config.make_pkg_config_path(self._installation_dir)

  def info_for_name(self, pkg_name):
    entry = self._db.find_package(pkg_name)
    if not entry:
      raise PackageNotFoundError('package %s not found' % (pkg_name))
    return entry.info

  def compilation_flags(self, pkg_names, static = False):
    pkg_config_path = self.pkg_config_path
    infos = [ self.info_for_name(pkg_name) for pkg_name in pkg_names ]
    pkg_config_names = object_util.flatten_list_of_lists([ pi.pkg_config_name for pi in infos ])
    cflags = pkg_config.cflags(pkg_config_names, PKG_CONFIG_PATH = pkg_config_path)
    libs = pkg_config.libs(pkg_config_names, PKG_CONFIG_PATH = pkg_config_path, static = static)
    return ( cflags, libs )

  def caca_compilation_flags(self, pkg_names, static = False):
    instructions = instruction_list.load_dir(self._compile_instructions_dir)

    #instructions
    #for inst in 
    
#    pkg_config_path = self.pkg_config_path
#    infos = [ self.info_for_name(pkg_name) for pkg_name in pkg_names ]
#    pkg_config_names = object_util.flatten_list_of_lists([ pi.pkg_config_name for pi in infos ])
#    cflags = pkg_config.cflags(pkg_config_names, PKG_CONFIG_PATH = pkg_config_path)
#    libs = pkg_config.libs(pkg_config_names, PKG_CONFIG_PATH = pkg_config_path, static = static)
    return None # ( cflags, libs )

  def install_tarball(self, pkg_tarball):

    pkg = package(pkg_tarball)

    if self.is_installed(pkg.info.name):
      raise PackageAlreadyInstallededError('package %s already installed' % (pkg.info.name))

    missing_requirements = self._missing_requirements(pkg, pkg.system)
    if missing_requirements:
      raise PackageMissingRequirementsError('package %s missing requirements: %s' % (pkg.info.name, ', '.join(missing_requirements)))
      
    conflicts = self._find_conflicts(pkg.files)
    if conflicts:
      conflict_packages = self._db.packages_with_files(conflicts)
      conflict_packages_str = ' '.join(conflict_packages)
      conflicts_str = ' '.join(conflicts)
      raise PackageFilesConflictError('conflicts found between \"%s\" and \"%s\": %s' % (pkg.info.name,
                                                                                         conflict_packages_str,
                                                                                         conflicts_str))
    pkg.extract_files(self._installation_dir)
    pkg.extract_env_files(self._env_dir, self._installation_dir)

    self._db.add_package(pkg.info, pkg.files)

  def uninstall_package(self, pkg_name):
    pkg = self._db.find_package(pkg_name)
    if not pkg:
      raise PackageNotFoundError('package %s not found' % (pkg_name))
    paths = [ path.join(self._installation_dir, f) for f in pkg.files ]
    file_util.remove(paths)
    self._db.remove_package(pkg_name)

  def list_all(self, include_version = False):
    return self._db.list_all(include_version = include_version)

  def is_installed(self, pkg_name):
    return self._db.find_package(pkg_name) != None

  def _find_conflicts(self, files):
    conflicts = []
    for f in files:
      if path.isfile(path.join(self._installation_dir, f)):
        conflicts.append(f)
    return sorted(conflicts)

  # FIXME: what about satisfying version and revision
  def _missing_requirements(self, pkg, system):
    requirements = pkg.info.requirements_for_system(system)
    if not requirements:
      return []
    missing_requirements = []
    for req in requirements:
      if not self._db.has_package(req.name):
        missing_requirements.append(req.name)
    return missing_requirements
    
  @classmethod
  def pkg_desc(clazz, tarball):
    return package(tarball).info

  @classmethod
  def package_files(clazz, tarball):
    return package(tarball).files

  def install_package(self, pkg_desc, build_target, artifact_manager,
                      allow_downgrade = False, force_install = False):
    assert artifact_manager.is_artifact_manager(artifact_manager)
    check.check_package_descriptor(pkg_desc)
    pkg = artifact_manager.package(pkg_desc, build_target)

    if self.is_installed(pkg.info.name):
      old_pkg_desc = self._db.find_package(pkg.info.name).info
      comparison = package_descriptor.full_name_cmp(old_pkg_desc, pkg_desc)
      if force_install:
        comparison = -1
      if comparison == 0:
        return False
      elif comparison < 0:
        self.uninstall_package(pkg.info.name)
        self.install_tarball(pkg.tarball)
        return True
      else:
        if allow_downgrade:
          self.uninstall_package(pkg.info.name)
          self.install_tarball(pkg.tarball)
          return True
        else:
          print(('warning: installed package %s newer than available package %s' % (old_pkg_desc.full_name, pkg_desc.full_name)))
        return False
    else:
      self.install_tarball(pkg.tarball)
      return True

  def install_packages(self, packages, build_target, artifact_manager, allow_downgrade = False, force_install = False):
    check.check_package_descriptor_seq(packages)
    assert artifact_manager.is_artifact_manager(artifact_manager)
    for pkg_desc in packages:
      self.install_package(pkg_desc, build_target, artifact_manager,
                           allow_downgrade = allow_downgrade,
                           force_install = force_install)

  def uninstall_packages(self, packages): #, build_target):
    # FIXME: nothing happens with build_target
    #check.check_package_descriptor_seq(packages)
    for pkg_name in packages:
      self.uninstall_package(pkg_name) #, build_target)

  def env_vars(self, pkg_names):
    'Return the environment variables for the given package names.'
    pkg_names = object_util.listify(pkg_names)
    infos = [ self.info_for_name(pkg_name) for pkg_name in pkg_names ]
    result = {}
    for pkg_desc in infos:
      os_env.update(result, self.__env_vars_for_one_package(pkg_desc))
    return result

  def __env_vars_for_one_package(self, pkg_desc):
    result = copy.deepcopy(pkg_desc.env_vars)
    variables = {
      'REBUILD_PACKAGE_ROOT_DIR': self._installation_dir,
      'REBUILD_PACKAGE_VERSION': str(pkg_desc.version),
      'REBUILD_PKG_NAME': pkg_desc.name,
    }
    
    for key, value in result.items():
      result[key] = variable.substitute(value, variables)
    return result

  def shell_env(self, packages):
    env = {
      os_env.LD_LIBRARY_PATH_VAR_NAME: self.lib_dir,
      'PATH': self.bin_dir,
      'PYTHONPATH': self._python_lib_dir,
      'PKG_CONFIG_PATH': pkg_config.make_pkg_config_path_for_unix_env(self._installation_dir)
    }
    all_env_vars = self.env_vars([ p.name for p in packages])
    os_env.update(env, all_env_vars)
    return env
  
  def export_variables_to_current_env(self, packages):
    all_env_vars = self.env_vars([ p.name for p in packages])
    for key, value in all_env_vars.items():
      os_env_var(key).value = value

  def load_tarball(self, filename, build_target, artifact_manager):
    'load a tarball and resturn a package object with requirements resolved according to packages currently installed.'
    if not package.package_is_valid(filename):
      raise RuntimeError('Not a valid package: %s' % (filename))
    pkg = package(filename)
    all_available_packages = artifact_manager.latest_available_packages(build_target)
    all_available_descriptors = package_list.descriptors(all_available_packages)
    all_available_descriptors = package_descriptor_list.filter_out_by_name(all_available_descriptors, pkg.info.name)
    all_descriptors = all_available_descriptors + [ pkg.info ]
    dependency_map = package_descriptor_list.dependency_map(all_descriptors)
    descriptor_map = package_descriptor_list.descriptor_map(all_descriptors)
    self._resolve_requirements(pkg.info, descriptor_map, dependency_map, build_target)
    return pkg

  @classmethod
  def _resolve_requirements(clazz, pkg_desc, descriptor_map, dependency_map, build_target):
    'resolve requirements for one pkg.'
    assert pkg_desc

    requirements = pkg_desc.requirements.resolve(build_target.system)
    requirements_names = [ req.name for req in requirements ]
    resolved_requirements = dependency_resolver.resolve_and_order_deps(requirements_names,
                                                                       descriptor_map,
                                                                       dependency_map)
    
    build_requirements = pkg_desc.build_requirements.resolve(build_target.system)
    build_requirements_names = [ req.name for req in build_requirements ]
    resolved_build_requirements = dependency_resolver.resolve_and_order_deps(build_requirements_names,
                                                                             descriptor_map,
                                                                             dependency_map)

    build_tool_requirements = pkg_desc.build_tool_requirements.resolve(build_target.system)
    build_tool_requirements_names = [ req.name for req in build_tool_requirements ]
    resolved_build_tool_requirements = dependency_resolver.resolve_and_order_deps(build_tool_requirements_names,
                                                                             descriptor_map,
                                                                             dependency_map)
    
    pkg_desc.resolved_requirements = resolved_requirements
    pkg_desc.resolved_build_requirements = resolved_build_requirements
    pkg_desc.resolved_build_tool_requirements = resolved_build_tool_requirements
