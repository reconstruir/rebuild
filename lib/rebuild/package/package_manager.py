#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# FIXME: theres no notion of transactions or anything else robust in this nice code

import copy, os.path as path, platform

from bes.system import log
from bes.archive import archive, archiver
from bes.common import check, object_util, string_util, variable
from bes.dependency import dependency_resolver
from bes.fs import file_util
from bes.system import os_env, os_env_var

from rebuild.base import build_system, requirement
from rebuild.base import package_descriptor, package_descriptor_list
from rebuild.instruction import instruction_list
from rebuild.pkg_config import pkg_config

from .artifact_manager import artifact_manager, ArtifactNotFoundError
from .package import package
from .package_db import package_db
from .package_db_entry import package_db_entry
from .env_dir import env_dir

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

  def __init__(self, root_dir, artifact_manager, log_tag = 'package_manager'):
    log.add_logging(self, log_tag)
    check.check_artifact_manager(artifact_manager)
    self._root_dir = root_dir
    self._artifact_manager = artifact_manager
    self._database_path = path.join(self._root_dir, 'db/packages.db')
    self._db = None
    self._installation_dir = path.join(self._root_dir, 'installation')
    self._env_dir = path.join(self._root_dir, 'env')
    self._lib_dir = path.join(self._installation_dir, 'lib')
    self._bin_dir = path.join(self._installation_dir, 'bin')
    self._include_dir = path.join(self._installation_dir, 'include')
    self._python_lib_dir = path.join(self._installation_dir, 'lib/python')
    self._share_dir = path.join(self._installation_dir, 'share')
    self._compile_instructions_dir = path.join(self._installation_dir, 'lib/rebuild_instructions')

  @property
  def root_dir(self): 
    return self._root_dir
    
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
  
  def descriptor_for_name(self, pkg_name):
    entry = self.db.find_package(pkg_name)
    if not entry:
      raise PackageNotFoundError('package %s not found' % (pkg_name))
    return entry.descriptor

  def compilation_flags(self, pkg_names, static = False):
    pkg_config_path = self.pkg_config_path
    descriptors = [ self.descriptor_for_name(pkg_name) for pkg_name in pkg_names ]
    pkg_config_names = object_util.flatten_list_of_lists([ pi.pkg_config_name for pi in descriptors ])
    cflags = pkg_config.cflags(pkg_config_names, PKG_CONFIG_PATH = pkg_config_path)
    libs = pkg_config.libs(pkg_config_names, PKG_CONFIG_PATH = pkg_config_path, static = static)
    return ( cflags, libs )

  def caca_compilation_flags(self, pkg_names, static = False):
    instructions = instruction_list.load_dir(self._compile_instructions_dir)

    #instructions
    #for inst in 
    
#    pkg_config_path = self.pkg_config_path
#    descriptors = [ self.descriptor_for_name(pkg_name) for pkg_name in pkg_names ]
#    pkg_config_names = object_util.flatten_list_of_lists([ pi.pkg_config_name for pi in descriptors ])
#    cflags = pkg_config.cflags(pkg_config_names, PKG_CONFIG_PATH = pkg_config_path)
#    libs = pkg_config.libs(pkg_config_names, PKG_CONFIG_PATH = pkg_config_path, static = static)
    return None # ( cflags, libs )

  @property
  def db(self):
    'Create the db on demand so that we dont put sqlite droppings all over if no transactions ever happen.'
    if not self._db:
      self._db = package_db(self._database_path)
    return self._db
  
  def install_tarball(self, pkg_tarball, hardness):
    self.log_i('installing tarball: %s for %s' % (pkg_tarball, ' '.join(hardness)))
    pkg = package(pkg_tarball)

    if self.is_installed(pkg.descriptor.name):
      raise PackageAlreadyInstallededError('package %s already installed' % (pkg.descriptor.name))
    missing_requirements = self._missing_requirements(pkg, pkg.build_target, hardness)
    
    if missing_requirements:
      raise PackageMissingRequirementsError('package %s missing requirements: %s' % (pkg.descriptor.name, ', '.join(missing_requirements)))
      
    conflicts = self._find_conflicts(pkg.files)
    if conflicts:
      conflict_packages = self.db.packages_with_files(conflicts)
      conflict_packages_str = ' '.join(conflict_packages)
      conflicts_str = ' '.join(conflicts)
      raise PackageFilesConflictError('conflicts found between \"%s\" and \"%s\": %s' % (pkg.descriptor.name,
                                                                                         conflict_packages_str,
                                                                                         conflicts_str))
    pkg.extract_files(self._installation_dir)
    pkg.extract_env_files(self._env_dir, self._installation_dir)

    entry = package_db_entry(pkg.metadata.name,
                             pkg.metadata.version,
                             pkg.metadata.revision,
                             pkg.metadata.epoch,
                             pkg.metadata.requirements,
                             pkg.metadata.properties,
                             pkg.metadata.files)
                             
    self.db.add_package(entry)

  def uninstall_package(self, pkg_name):
    self.log_i('uninstalling package: %s' % (pkg_name))
    pkg = self.db.find_package(pkg_name)
    if not pkg:
      raise PackageNotFoundError('package %s not found' % (pkg_name))
    paths = [ path.join(self._installation_dir, f) for f in pkg.files.filenames() ]
    file_util.remove(paths)
    self.db.remove_package(pkg_name)

  def list_all(self, include_version = False):
    return self.db.list_all(include_version = include_version)

  def is_installed(self, pkg_name):
    return self.db.find_package(pkg_name) != None

  def _find_conflicts(self, files):
    conflicts = []
    for f in files:
      if path.isfile(path.join(self._installation_dir, f)):
        conflicts.append(f)
    return sorted(conflicts)

  def _missing_requirements(self, pkg, build_target, hardness):
    requirements = pkg.descriptor.requirements.filter_by_system(build_target.system).filter_by_hardness(hardness).names()
    resolved_deps = self._artifact_manager.resolve_deps_poto(requirements, build_target, hardness, False)

    if not resolved_deps:
      return []
    missing_requirements = []
    for req in resolved_deps:
      if not self.db.has_package(req.name):
        missing_requirements.append(req.name)
    return missing_requirements
  
  @classmethod
  def pkg_desc(clazz, tarball):
    return package(tarball).descriptor

  @classmethod
  def package_files(clazz, tarball):
    return package(tarball).files.filenames()

  def install_package(self, pkg_desc, build_target, hardness,
                      allow_downgrade = False, force_install = False):
    self.log_i('installing package: %s for %s' % (str(pkg_desc), ' '.join(hardness)))
    check.check_package_descriptor(pkg_desc)
    pkg = self._artifact_manager.package(pkg_desc, build_target)

    if self.is_installed(pkg.descriptor.name):
      old_pkg_entry = self.db.find_package(pkg.descriptor.name)
      old_pkg_entry_desc = old_pkg_entry.descriptor
      comparison = package_descriptor.full_name_cmp(old_pkg_entry_desc, pkg_desc)
      self.log_d('installing package: comparison=%s' % (comparison))
      if force_install:
        if old_pkg_entry.checksum != pkg.metadata.checksum:
          self.log_i('installing package: checksums changed: %s' % (str(pkg_desc)))
          comparison = -1
      if comparison == 0:
        return False
      elif comparison < 0:
        self.uninstall_package(pkg.descriptor.name)
        self.install_tarball(pkg.tarball, hardness)
        return True
      else:
        if allow_downgrade:
          self.uninstall_package(pkg.descriptor.name)
          self.install_tarball(pkg.tarball, hardness)
          return True
        else:
          print('warning: installed package %s newer than available package %s' % (old_pkg_entry_desc.full_name, pkg_desc.full_name))
        return False
    else:
      self.install_tarball(pkg.tarball, hardness)
      return True

  def install_packages(self, packages, build_target, hardness, allow_downgrade = False, force_install = False):
    check.check_package_descriptor_seq(packages)
    
    for pkg_desc in packages:
      self.install_package(pkg_desc, build_target, hardness,
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
    descriptors = [ self.descriptor_for_name(pkg_name) for pkg_name in pkg_names ]
    result = {}
    for pkg_desc in descriptors:
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
      result[key] = variable.substitute(value or '', variables)
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

  def transform_env(self, env):
    return env_dir(self._env_dir).transform_env(env)
  
  def export_variables_to_current_env(self, packages):
    all_env_vars = self.env_vars([ p.name for p in packages])
    for key, value in all_env_vars.items():
      os_env_var(key).value = value

  def load_tarball(self, filename, build_target):
    'load a tarball and resturn a package object with requirements resolved according to packages currently installed.'
    if not package.package_is_valid(filename):
      raise RuntimeError('Not a valid package: %s' % (filename))
    return package(filename)
