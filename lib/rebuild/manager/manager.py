#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import algorithm
from bes.fs import file_util
from bes.common import check, object_util
from bes.system import log, os_env
from rebuild.base import build_blurb
from bes.dependency import dependency_resolver
from rebuild.package import package_manager
from collections import namedtuple
from .manager_config import manager_config
from .manager_script import manager_script

class manager(object):

  DEFAULT_ROOT_DIR = path.expanduser('~/.rebbe')

  CONFIG_FILENAME = 'config'
  
  def __init__(self, artifact_manager, build_target, root_dir = None):
    log.add_logging(self, 'remanage')
    build_blurb.add_blurb(self, label = 'remanage')
    check.check_artifact_manager(artifact_manager)
    check.check_build_target(build_target)
    self.root_dir = path.abspath(root_dir or self.DEFAULT_ROOT_DIR)
    self.build_target = build_target
    self.artifact_manager = artifact_manager
    self.package_managers = {}
    self.config_filename = path.join(self.root_dir, self.CONFIG_FILENAME)

  @classmethod
  def _project_subpath(clazz, project_name, system):
    return path.join(project_name, system)
    
  def _project_root_dir(self, project_name, system):
    subpath = self._project_subpath(project_name, system)
    return path.join(self.root_dir, subpath)
    
  def _package_manager(self, project_name, system):
    subpath = self._project_subpath(project_name, system)
    if subpath not in self.package_managers:
      self.package_managers[project_name] = package_manager(path.join(self.root_dir, subpath),
                                                            self.artifact_manager,
                                                            log_tag = 'remanage.%s' % (project_name))
    return self.package_managers[project_name]

  def update_packages(self, project_name, packages, build_target, allow_downgrade = False, force_install = False):
    pm = self._package_manager(project_name, build_target.system)
    pm.install_packages(packages, build_target, [ 'RUN' ], allow_downgrade = allow_downgrade, force_install = force_install)
    pm.ensure_shell_framework()
    
  def installed_packages(self, project_name, build_target):
    pm = self._package_manager(project_name, build_target.system)
    return pm.list_all()

  ResolveResult = namedtuple('ResolveResult', 'available,missing,resolved')
  def resolve_packages(self, package_names, build_target):
    self.log_i('resolving: %s' % (' '.join(package_names)))
    resolved_deps = self.artifact_manager.resolve_deps(package_names, build_target, ['RUN'], True)
    resolved_names = [ desc.name for desc in resolved_deps ]
    available_packages = self.artifact_manager.available_packages(build_target)
    available_names = [ p.package_descriptor.name for p in available_packages ]
    missing_packages = dependency_resolver.check_missing(available_names, package_names)
    if missing_packages:
      return self.ResolveResult(available_packages, missing_packages, [])
    resolved = self.artifact_manager.resolve_packages(resolved_names, build_target)
    resolved_descriptors = [ r.package_descriptor for r in resolved ]
    self.log_i('done resolving')
    return self.ResolveResult(available_packages, [], resolved_descriptors)

  def resolve_and_update_packages(self, project_name, packages, build_target, allow_downgrade = False, force_install = False):
    resolve_rv = self.resolve_packages(packages, build_target)
    if resolve_rv.missing:
      self.blurb('missing artifacts at %s: %s' % (self.artifact_manager.root_dir, ' '.join(resolve_rv.missing)))
      return []
    self.update_packages(project_name, resolve_rv.resolved, build_target, allow_downgrade = allow_downgrade, force_install = force_install)
    return [ pi.name for pi in resolve_rv.resolved ]

  def uninstall_packages(self, project_name, packages, build_target):
    self.log_i('%s - uninstalling: %s' % (package_name, ' '.join(packages)))
    # FIXME: no dependents handling
    pm = self._package_manager(project_name, build_target)
    pm.uninstall_packages(packages) #, build_target)
    return True

  def _load_config(self, build_target):
    self.log_i('loading config: %s' % (self.config_filename))
    if not path.exists(self.config_filename):
      raise RuntimeError('config file does not exist: %s' % (self.config_filename))
    config = manager_config()
    config.load_file(self.config_filename, build_target)
    return config

  def update_from_config(self, build_target, wipe, project_name = None, allow_downgrade = False, force_install = False):
    config = self._load_config(build_target)
    want_specific_project = project_name is not None
    valid_project_names = sorted(config.keys())
    if want_specific_project and project_name not in valid_project_names:
      self.blurb('invalid project \"%s\" - should be one of: %s' % (project_name, ' '.join(valid_project_names)), fit = True)
      return False

    if want_specific_project:
      return self._update_project_from_config(build_target, wipe, config[project_name], project_name, allow_downgrade, force_install)
    else:
      for project_name, values in config.items():
        if not self._update_project_from_config(build_target, wipe, values, project_name, allow_downgrade, force_install):
          return False
      return True
  
  def _update_project_from_config(self, build_target, wipe, values, project_name, allow_downgrade, force_install):
    self.log_i('%s - updating' % (project_name))
    if wipe:
      self._wipe_project_dir(project_name, build_target)
    resolved_packages = self.resolve_and_update_packages(project_name,
                                                         values['packages'],
                                                         build_target,
                                                         allow_downgrade = allow_downgrade,
                                                         force_install = force_install)
    if not resolved_packages:
      self.blurb('failed to update %s from %s' % (project_name, self.config_filename))
      return False
    installed_packages = self.installed_packages(project_name, build_target)
    removed_packages = list(set(installed_packages).difference(set(resolved_packages)))
    self.log_i('%s - installed packages: %s' % (project_name, ' '.join(installed_packages)))
    self.log_i('%s - removed packages: %s' % (project_name, ' '.join(removed_packages)))
    if removed_packages:
      self.uninstall_packages(project_name, removed_packages, build_target)
    self._save_system_setup_scripts(project_name, build_target)
    return True
  
  SETUP_SYSTEM_SCRIPT_TEMPLATE = '''
_this_file="$( command readlink "$BASH_SOURCE" )" || _this_file="$BASH_SOURCE"
_root="${_this_file%/*}"
if [ "$_root" == "$_this_file" ]; then
  _root=.
fi
_@NAME@_root="$( command cd -P "$_root" > /dev/null && command pwd -P )"
unset _this_file
unset _root

_@NAME@_setup()
{
  local _root=${_@NAME@_root}
  local _prefix=${_root}/stuff
  export PATH=${_prefix}/bin:${PATH}
  export PYTHONPATH=${_prefix}/lib/python:${PYTHONPATH}
  export PKG_CONFIG_PATH=${_prefix}/lib/pkgconfig:${PKG_CONFIG_PATH}
  export @LIBRARY_PATH@=${_prefix}/lib:${@LIBRARY_PATH@}
  export MANPATH=${_prefix}/man:${_prefix}/share/man:${MANPATH}
  local _env_dir=$_root/env
  if [ -d $_env_dir -a -n "$(ls -A $_env_dir/*.sh)" ]; then
    for f in $(find $_env_dir -name "*.sh" -maxdepth 1); do
      source "$f"
    done
  fi  
}
'''

  SETUP_SCRIPT_TEMPLATE = '''
_this_file="$( command readlink "$BASH_SOURCE" )" || _this_file="$BASH_SOURCE"
_root="${_this_file%/*}"
if [ "$_root" == "$_this_file" ]; then
  _root=.
fi
_@NAME@_root="$( command cd -P "$_root" > /dev/null && command pwd -P )"
unset _this_file
unset _root

_rebuild_system_name()
{
  local _system='unknown'
  case $(uname) in
    Darwin)
      _system=macos
      ;;
	  Linux)
      _system=linux
      ;;
	esac
  echo ${_system}
}

@NAME@_setup()
{
  local _system=$(_rebuild_system_name)
  local _root=${_@NAME@_root}
  local _system_root=${_root}/${_system}
  local _prefix=${_system_root}/stuff
  export PATH=${_prefix}/bin:${PATH}
  export PYTHONPATH=${_prefix}/lib/python:${PYTHONPATH}
  export PKG_CONFIG_PATH=${_prefix}/lib/pkgconfig:${PKG_CONFIG_PATH}
  export DYLD_LIBRARY_PATH=${_prefix}/lib:${DYLD_LIBRARY_PATH}
  export MANPATH=${_prefix}/man:${_prefix}/share/man:${MANPATH}
  local _env_dir=$_system_root/env
  if [ -d $_env_dir ]; then
    for f in $(find $_env_dir -name "*.sh" -maxdepth 1); do
      source "$f"
    done
  fi  
}
'''

  SYSTEM_RUN_SCRIPT_TEMPLATE = '''#!/bin/bash
source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/setup.sh"
@NAME@_setup
exec ${1+"$@"}
'''

  def _save_system_setup_scripts(self, project_name, build_target):
    system_setup_script = manager_script(self.SETUP_SYSTEM_SCRIPT_TEMPLATE, 'setup.sh')
    system_run_script = manager_script(self.SYSTEM_RUN_SCRIPT_TEMPLATE, 'run.sh')
    setup_script = manager_script(self.SETUP_SCRIPT_TEMPLATE, 'setup.sh')
    pm = self._package_manager(project_name, build_target.system)
    variables = {
      '@LIBRARY_PATH@': os_env.LD_LIBRARY_PATH_VAR_NAME,
      '@NAME@': project_name,
      '@SYSTEM@': build_target.system,
    }
    system_setup_script.save(pm.root_dir, variables)
    system_run_script.save(pm.root_dir, variables)
    parent_dir = path.join(pm.root_dir, '..')
    setup_script.save(parent_dir, variables)
    system_run_script.save(parent_dir, variables)
  
  def config(self, build_target):
    return self._load_config(build_target)

  def _wipe_project_dir(self, project_name, build_target):
    project_root_dir = self._project_root_dir(project_name, build_target.system)
    self.blurb('wiping root dir: %s' % (project_root_dir))
    self.log_i('%s - wiping: %s' % (project_name, project_root_dir))
    file_util.remove(project_root_dir)

  def remove_checksums(self, packages, build_target):
    assert False
    packages = object_util.listify(packages)
    check.check_package_descriptor_seq(packages)
    checksum_dirs = [ self.checksum_dir(package_info, build_target) for package_info in packages ]
    file_util.remove(checksum_dirs)
