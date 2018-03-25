#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import algorithm
from bes.fs import file_util
from bes.common import check, dict_util, object_util
from bes.system import os_env
from rebuild.base import build_blurb, build_target, package_descriptor
from bes.dependency import dependency_resolver
from rebuild.package import artifact_manager, package, package_manager, package_list
from collections import namedtuple
from .rebuild_manager_config import rebuild_manager_config
from .rebuild_manager_script import rebuild_manager_script

class rebuild_manager(object):

  DEFAULT_ROOT_DIR = path.expanduser('~/.rebbe')

  CONFIG_FILENAME = 'config'
  
  def __init__(self, artifact_manager, root_dir = None):
    check.check_artifact_manager(artifact_manager)
    build_blurb.add_blurb(self, label = 'build')
    self.root_dir = path.abspath(root_dir or self.DEFAULT_ROOT_DIR)
    self.artifact_manager = artifact_manager
    self.package_managers = {}
    self.config_filename = path.join(self.root_dir, self.CONFIG_FILENAME)
    
  def _package_manager(self, project_name):
    if project_name not in self.package_managers:
      root_dir = path.join(self.root_dir, project_name)
      self.package_managers[project_name] = package_manager(root_dir, self.artifact_manager)
    return self.package_managers[project_name]

  def update_packages(self, project_name, packages, build_target, allow_downgrade = False, force_install= False):
    pm = self._package_manager(project_name)
    pm.install_packages(packages, build_target, [ 'RUN' ], allow_downgrade = allow_downgrade, force_install = force_install)

  def project_root_dir(self, project_name):
    return self._package_manager(project_name).root_dir

  def installed_packages(self, project_name, build_target):
    pm = self._package_manager(project_name)
    return pm.list_all()

  ResolveResult = namedtuple('ResolveResult', 'available,missing,resolved')
  def resolve_packages(self, packages, build_target):
    resolved_names = algorithm.unique(self.artifact_manager.resolve_deps_caca_run(packages, build_target) + packages)
    available_packages = self.artifact_manager.available_packages(build_target)
    available_names = [ p.info.name for p in available_packages ]
    missing_packages = dependency_resolver.check_missing(available_names, packages)
    if missing_packages:
      return self.ResolveResult(available_packages, missing_packages, [])
    resolved = self.artifact_manager.resolve_packages(resolved_names, build_target)
    resolved_infos = [ r.info for r in resolved ]
    return self.ResolveResult(available_packages, [], resolved_infos)

  def resolve_and_update_packages(self, project_name, packages, build_target, allow_downgrade = False, force_install = False):
    resolve_rv = self.resolve_packages(packages, build_target)
    if resolve_rv.missing:
      self.blurb('missing artifacts at %s: %s' % (self.artifact_manager.publish_dir, ' '.join(resolve_rv.missing)))
      return []
    self.update_packages(project_name, resolve_rv.resolved, build_target, allow_downgrade = allow_downgrade, force_install = force_install)
    return [ pi.name for pi in resolve_rv.resolved ]

  def uninstall_packages(self, project_name, packages, build_target):
    # FIXME: no dependents handling
    pm = self._package_manager(project_name)
    pm.uninstall_packages(packages) #, build_target)
    return True

  def _load_config(self, build_target):
    if not path.exists(self.config_filename):
      raise RuntimeError('config file does not exist: %s' % (self.config_filename))
    config = rebuild_manager_config()
    config.load_file(self.config_filename, build_target)
    return config

  def update_from_config(self, build_target, project_name = None, allow_downgrade = False, force_install = False):
    config = self._load_config(build_target)

    want_specific_project = project_name is not None
    if want_specific_project and project_name not in config.keys():
      raise RuntimeError('Unknown project: %s' % (project_name))

    if want_specific_project:
      return self._update_project_from_config(build_target, config[project_name], project_name, allow_downgrade, force_install)
    else:
      for project_name, values in config.items():
        if not self._update_project_from_config(build_target, values, project_name, allow_downgrade, force_install):
          return False
      return True
  
  def _update_project_from_config(self, build_target, values, project_name, allow_downgrade, force_install):
    print('project_name: %s; values: %s' % (project_name, values))
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
    if removed_packages:
      self.uninstall_packages(project_name, removed_packages, build_target)
    self._save_setup_scripts(project_name)
    return True
  
  SETUP_SCRIPT_TEMPLATE = '''
@NAME@_prefix()
{
  echo "@PREFIX@"
  return 0
}

@NAME@_setup()
{
  local _prefix=$(@NAME@_prefix)
  export PATH=${_prefix}/bin:${PATH}
  export PYTHONPATH=${_prefix}/lib/python:${PYTHONPATH}
  export PKG_CONFIG_PATH=${_prefix}/lib/pkgconfig:${PKG_CONFIG_PATH}
  export @LIBRARY_PATH@=${_prefix}/lib:${@LIBRARY_PATH@}
  export MANPATH=${_prefix}/man:${_prefix}/share/man:${MANPATH}
  local _env_dir=$_prefix/../env
  if [ -d $_env_dir -a -n "$(ls -A $_env_dir)" ]; then
    for f in $_env_dir/*; do
      source "$f"
    done
  fi  
}
'''

  RUN_SCRIPT_TEMPLATE = '''#!/bin/bash
source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/setup.sh"
@NAME@_setup
exec ${1+"$@"}
'''

  def _save_setup_scripts(self, project_name):
    setup_script = rebuild_manager_script(self.SETUP_SCRIPT_TEMPLATE, 'setup.sh')
    run_script = rebuild_manager_script(self.RUN_SCRIPT_TEMPLATE, 'run.sh')
    pm = self._package_manager(project_name)
    variables = {
      '@PREFIX@': pm.installation_dir,
      '@LIBRARY_PATH@': os_env.LD_LIBRARY_PATH_VAR_NAME,
      '@NAME@': project_name,
    }
    setup_script.save(pm.root_dir, variables)
    run_script.save(pm.root_dir, variables)
  
  def config(self, build_target):
    return self._load_config(build_target)

  def wipe_project_dir(self, project_name):
    project_root_dir = self.project_root_dir(project_name)
    self.blurb('wiping root dir: %s' % (project_root_dir))
    file_util.remove(project_root_dir)

  def remove_checksums(self, packages, build_target):
    assert False
    packages = object_util.listify(packages)
    check.check_package_descriptor_seq(packages)
    checksum_dirs = [ self.checksum_dir(package_info, build_target) for package_info in packages ]
    file_util.remove(checksum_dirs)

  def dep_map(self, build_target):
    'Return a map of dependencies for the given build_target.'
    available_packages = self.artifact_manager.available_packages(build_target)
    available_packages = package_list.latest_versions(available_packages)
    dep_map = {}
    for package in available_packages:
      existing_package = dep_map.get(package.info.name, None)
      if existing_package:
        raise RuntimeError('package \"%s\" is already in dep_map (multiple versions) as \"%s\""' % (package.info, existing_package))
      dep_map[package.info.name] = package.info.requirements_names_for_system(build_target.system)
    return dep_map
