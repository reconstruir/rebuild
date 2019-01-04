#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# FIXME: theres no notion of transactions or anything else robust in this nice code

import copy, os.path as path, platform

from bes.system import log
from bes.archive import archive, archiver
from bes.common import check, object_util, string_util, variable
from bes.dependency import dependency_resolver
from bes.fs import file_path, file_util
from bes.system import os_env
from bes.env import env_dir, shell_framework

from rebuild.base import build_system, requirement
from rebuild.base import package_descriptor, package_descriptor_list
from rebuild.instruction import instruction_list
from rebuild.pkg_config import pkg_config
from rebuild.base import build_blurb

from .package import package
from .package_db import package_db
from .package_db_entry import package_db_entry
from .package_install_options import package_install_options
from .db_error import *

class PackageFilesConflictError(Exception):
  def __init__(self, message):
    super(PackageFilesConflictError, self).__init__()
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
    build_blurb.add_blurb(self, label = 'retool')
    if artifact_manager:
      check.check_artifact_manager(artifact_manager)
    self._root_dir = root_dir
    self._artifact_manager = artifact_manager
    self._database_path = path.join(self._root_dir, 'db/packages.db')
    self._db = None
    self._installation_dir = path.join(self._root_dir, 'stuff')
    self._env_dir = path.join(self._root_dir, 'env')
    self._lib_dir = path.join(self._installation_dir, 'lib')
    self._bin_dir = path.join(self._installation_dir, 'bin')
    self._include_dir = path.join(self._installation_dir, 'include')
    self._python_lib_dir = path.join(self._installation_dir, 'lib/python')
    self._share_dir = path.join(self._installation_dir, 'share')
    self._compile_instructions_dir = path.join(self._installation_dir, 'lib/rebuild_instructions')
    self._shell_framework_dir = path.join(self._env_dir, 'framework')
    self._shell_env = {
      os_env.LD_LIBRARY_PATH_VAR_NAME: self._lib_dir,
      'PATH': self._bin_dir,
      'PYTHONPATH': self._python_lib_dir,
      'PKG_CONFIG_PATH': pkg_config.make_pkg_config_path_for_unix_env(self._installation_dir)
    }
    
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

  def tool_exe(self, tool_name):
    exe = path.join(self.bin_dir, tool_name)
    if not file_path.is_executable(exe):
      return None
    return exe
  
  @property
  def include_dir(self):
    return self._include_dir

  @property
  def share_dir(self):
    return self._share_dir

  @property
  def pkg_config_path(self):
    return pkg_config.make_pkg_config_path(self._installation_dir)
  
  @property
  def shell_framework_dir(self):
    return self._shell_framework_dir
  
  def descriptor_for_name(self, pkg_name):
    entry = self.db.find_package(pkg_name)
    if not entry:
      raise NotInstalledError('package %s not found' % (pkg_name))
    return entry.descriptor

  def compilation_flags(self, package_names, static = False):
    pkg_config_path = self.pkg_config_path
    descriptors = [ self.descriptor_for_name(pkg_name) for pkg_name in package_names ]
    pkg_config_names = object_util.flatten_list_of_lists([ pi.pkg_config_name for pi in descriptors ])
    cflags = pkg_config.cflags(pkg_config_names, PKG_CONFIG_PATH = pkg_config_path)
    libs = pkg_config.libs(pkg_config_names, PKG_CONFIG_PATH = pkg_config_path, static = static)
    return ( cflags, libs )

  def caca_compilation_flags(self, package_names, static = False):
    instructions = instruction_list.load_dir(self._compile_instructions_dir)

    #instructions
    #for inst in 
    
#    pkg_config_path = self.pkg_config_path
#    descriptors = [ self.descriptor_for_name(pkg_name) for pkg_name in package_names ]
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
  
  def install_tarball(self, pkg_tarball, metadata, hardness):
    check.check_string(pkg_tarball)
    check.check_package_metadata(metadata)
    self.log_i('installing tarball: %s for %s' % (pkg_tarball, ' '.join(hardness)))

    needs_download = self._artifact_manager.needs_download(metadata.artifact_descriptor)
    self.log_d('needs_download=%s package=%s' % (needs_download, str(metadata.artifact_descriptor)))
    if needs_download:
      self.log_i('downloading package: %s' % (str(metadata.artifact_descriptor)))
      self.blurb_verbose('downloading %s' % (str(metadata.artifact_descriptor)))
      self._artifact_manager.download(metadata.artifact_descriptor)
      
    self.log_i('installing tarball: %s for %s' % (pkg_tarball, ' '.join(hardness)))
    self.blurb_verbose('installing %s' % (str(metadata.artifact_descriptor)))
    pkg = package(pkg_tarball)

    if self.is_installed(pkg.package_descriptor.name):
      raise AlreadyInstalledError('package %s already installed' % (pkg.package_descriptor.name), pkg)
    missing_requirements = self._missing_requirements(pkg, pkg.build_target, hardness)
    
    if missing_requirements:
      raise PackageMissingRequirementsError('package %s missing requirements: %s' % (pkg.package_descriptor.name, ', '.join(missing_requirements)))
      
    conflicts = self._find_conflicts(pkg.files)
    if conflicts:
      conflict_packages = self.db.packages_with_files(conflicts)
      conflict_packages_str = ' '.join(conflict_packages)
      conflicts_str = ' '.join(conflicts)
      raise PackageFilesConflictError('conflicts found between \"%s\" and \"%s\": %s' % (pkg.package_descriptor.name,
                                                                                         conflict_packages_str,
                                                                                         conflicts_str))
    pkg.extract(self._root_dir, 'stuff', 'env')
    self.ensure_shell_framework()
    entry = package_db_entry(pkg.metadata.name,
                             pkg.metadata.version,
                             pkg.metadata.revision,
                             pkg.metadata.epoch,
                             pkg.metadata.requirements,
                             pkg.metadata.properties,
                             pkg.metadata.manifest)
                             
    self.db.add_package(entry)

  def ensure_shell_framework(self):
    ef = shell_framework()
    ef.extract(self._shell_framework_dir, 'rebuild')
    
  def uninstall_package(self, pkg_desc):
    check.check_package_descriptor(pkg_desc)
    self.log_i('uninstalling_package: pkg_desc=%s' % (pkg_desc.full_name))
    pkg = self.db.find_package(pkg_desc.name)
    if not pkg:
      raise NotInstalledError('package %s not found' % (pkg_desc.name))
    paths = [ path.join(self._installation_dir, f) for f in pkg.manifest.files.filenames() ]
    paths.extend([ path.join(self._env_dir, f) for f in pkg.manifest.env_files.filenames() ])
    file_util.remove(paths)
    self.db.remove_package(pkg_desc.name)

  def list_all_names(self, include_version = False):
    return self.db.list_all_names(include_version = include_version)

  def list_all_descriptors(self):
    return self.db.list_all_descriptors()

  def is_installed(self, pkg_name):
    return self.db.find_package(pkg_name) != None

  def _find_conflicts(self, files):
    conflicts = []
    for f in files:
      if path.isfile(path.join(self._installation_dir, f)):
        conflicts.append(f)
    return sorted(conflicts)

  def _missing_requirements(self, pkg, build_target, hardness):
    requirements = pkg.package_descriptor.requirements.filter_by_system(build_target.system).filter_by_hardness(hardness).names()
    resolved_deps = self._artifact_manager.resolve_deps(requirements, build_target, hardness, False)

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
  def package_manifest(clazz, tarball):
    return package(tarball).files.filenames()

  def install_package(self, pkg_desc, build_target, hardness, options = None):
    check.check_package_descriptor(pkg_desc)
    check.check_package_install_options(options, allow_none = True)
    self.log_i('install_package: pkg_desc=%s; options=%s' % (pkg_desc, options))
    result = self._install_package(pkg_desc, build_target, hardness, options)
    return result
    
  def _install_package(self, pkg_desc, build_target, hardness, options):
    options = options or package_install_options()
    pkg = self._artifact_manager.find_by_package_descriptor(pkg_desc, build_target, relative_filename = False)
    if not pkg:
      raise RuntimeError('Failed to find package in artifact manager: %s - %s' % (str(pkg_desc), str(build_target)))
    if self.is_installed(pkg.name):
      self.log_i('install_package: %s for %s' % (pkg_desc.full_name, ' '.join(hardness)))
      old_pkg_entry = self.db.find_package(pkg.name)
      old_pkg_entry_desc = old_pkg_entry.descriptor
      comparison = package_descriptor.full_name_cmp(old_pkg_entry_desc, pkg_desc)
      if options.allow_same_version:
        if self._contents_checksum_changed(old_pkg_entry, pkg):
          comparison = -1
      if comparison == 0:
        self.log_i('install_package: no change needed: %s' % (pkg_desc.name))
        return False
      elif comparison < 0:
        self.log_i('install_package: upgrading from %s to %s' % (old_pkg_entry_desc.full_name,
                                                                 pkg.full_name))
        self.uninstall_package(pkg.package_descriptor)
        self.install_tarball(pkg.filename, pkg, hardness)
        return True
      else:
        if options.allow_downgrade:
          self.log_i('install_package: downgrading from %s to %s' % (old_pkg_entry_desc.full_name,
                                                                     pkg.full_name))
          self.uninstall_package(pkg.package_descriptor)
          self.install_tarball(pkg.filename, pkg, hardness)
          return True
        else:
          print('warning: installed package %s newer than available package %s' % (old_pkg_entry_desc.full_name,
                                                                                   pkg_desc.full_name))
        return False
    else:
      self.log_i('install_package: first install: %s' % (pkg.filename))
      self.install_tarball(pkg.filename, pkg, hardness)
      return True

  @classmethod
  def _contents_checksum_changed(clazz, old_pkg_entry, new_pkg):
    check.check_package_db_entry(old_pkg_entry)
    check.check_package_metadata(new_pkg)
    old_desc = old_pkg_entry.descriptor
    old_contents_checksum = old_pkg_entry.manifest.contents_checksum
    new_contents_checksum = new_pkg.manifest.contents_checksum
    contents_checksum_changed = old_contents_checksum != new_contents_checksum
    if contents_checksum_changed:
      clazz.log_i('install_package: files changed: %s old=%s new=%s' % (old_desc.name,
                                                                        old_contents_checksum,
                                                                        new_contents_checksum))
    return contents_checksum_changed
      
  def install_packages(self, packages, build_target, hardness, options = None):
    check.check_package_descriptor_list(packages)
    check.check_package_install_options(options, allow_none = True)
    
    for pkg_desc in packages:
      self.install_package(pkg_desc, build_target, hardness, options)

  def uninstall_packages(self, packages): #, build_target):
    # FIXME: nothing happens with build_target
    check.check_package_descriptor_list(packages)
    for pkg_desc in packages:
      self.uninstall_package(pkg_desc) #, build_target)

  def package_env_files(self, package_names):
    'Return a list of env files for the given packages in the same order as packages.'
    check.check_string_seq(package_names)
    result = []
    for package_name in package_names:
      entry = self.db.find_package(package_name)
      assert entry
      result.extend([ f.filename for f in entry.manifest.env_files ])
    return result
  
  def transform_env(self, env, package_names):
    check.check_string_seq(package_names)
    env = env or { 'PATH': os_env.DEFAULT_SYSTEM_PATH }
    if not 'PATH' in env:
      env = copy.deepcopy(env)
      env['PATH'] = os_env.DEFAULT_SYSTEM_PATH
    result = copy.deepcopy(env)
    os_env.update(result, self._shell_env, prepend = False)
    files = self.package_env_files(package_names)
    if not files:
      return result
    if not path.isdir(self._env_dir):
      return result
    ed = env_dir(self._env_dir, files = files)
    result = ed.transform_env(result)
    for key, value in result.items():
      if key.startswith('_REBUILD'):
        del result[key]
    return result

  def expose_env(self, package_names):
    old_env = os_env.clone_current_env()
    new_env = self.transform_env(old_env, package_names)
    for key, value in new_env.items():
      os.environ[key] = value
  
  def load_tarball(self, filename, build_target):
    'load a tarball and resturn a package object with requirements resolved according to packages currently installed.'
    if not package.is_package(filename):
      raise RuntimeError('Not a valid package: %s' % (filename))
    return package(filename)

  def dep_map(self):
    'Return a dependency map of the packages currently installed.'
    return self.db.dep_map()

  def descriptors_for_names(self, names):
    check.check_string_seq(names)
    return self.db.descriptors_for_names(sorted(names))
