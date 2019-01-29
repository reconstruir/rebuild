#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.env import shell_framework
from bes.fs import file_path, file_util
from bes.system import log, os_env
from rebuild.base import build_blurb, build_version, package_descriptor_list
from bes.dependency import dependency_resolver
from rebuild.package import package_manager
from collections import namedtuple

from .venv_shell_script import venv_shell_script
from .venv_config import venv_config
from .venv_install_options import venv_install_options

class venv_manager(object):

  def __init__(self, config, artifact_manager, build_target, root_dir):
    log.add_logging(self, 'venv')
    build_blurb.add_blurb(self, label = 'venv')
    check.check_venv_config(config, allow_none = True)
    check.check_artifact_manager(artifact_manager)
    check.check_build_target(build_target)
    check.check_string(root_dir)
    self._config = config
    self._artifact_manager = artifact_manager
    self._build_target = build_target
    self._root_dir = path.abspath(root_dir)
    self._package_managers = {}

  @classmethod
  def _project_subpath(clazz, project_name, build_target):
    # Remove the release/debug part of the path since its useless in this context
    p = file_path.join(file_path.split(build_target.build_path)[0:-1])
    return path.join(project_name, p)
    
  def _project_root_dir(self, project_name, build_target):
    subpath = self._project_subpath(project_name, build_target)
    return path.join(self._root_dir, subpath)
    
  def _package_manager(self, project_name, build_target):
    check.check_build_target(build_target)
    subpath = self._project_subpath(project_name, build_target)
    if subpath not in self._package_managers:
      self._package_managers[project_name] = package_manager(path.join(self._root_dir, subpath),
                                                            self._artifact_manager,
                                                            log_tag = 'package_manager.%s' % (project_name))
    return self._package_managers[project_name]

  def _update_packages(self, project_name, packages, build_target, options = None):
    check.check_string(project_name)
    check.check_package_descriptor_list(packages)
    check.check_build_target(build_target)
    options = options or venv_install_options()
    check.check_venv_install_options(options)
    pm = self._package_manager(project_name, build_target)
    pm.install_packages(packages, build_target, [ 'RUN' ], options.package_install_options)
    pm.ensure_shell_framework()
    
  def installed_packages(self, project_name, build_target):
    pm = self._package_manager(project_name, build_target)
    return pm.list_all_descriptors()

  def installed_packages_names(self, project_name, build_target, include_version = False):
    pm = self._package_manager(project_name, build_target)
    return pm.list_all_names(include_version = include_version)

  _resolve_result = namedtuple('_resolve_result', 'available, missing, resolved')
  def _resolve_packages(self, build_target, requirements):
    check.check_requirement_list(requirements)
    check.check_build_target(build_target)
#    available = self._artifact_manager.list_all_by_descriptor(None) #build_target)
#    for a in available:
#      self.log_d('_resolve_packages: AVAILABLE: %s' % (str(a)))
    self.log_d('_resolve_packages: build_target=%s; requirements=%s' % (build_target.build_path, requirements))
    resolve_rv = self._artifact_manager.poto_resolve_deps(requirements, build_target, ['RUN'], True)

    if resolve_rv.missing:
      rdict = requirements.to_dict()
      for package in resolve_rv.missing:
        self.blurb('missing artifact: %s' % (str(rdict[package])))
      self.blurb('    build target: %s' % (build_target.build_path))
      self.blurb(' config filename: %s' % (self._config.filename))
#      self.blurb('         project: %s' % (project_name))
      self.blurb('artifact manager: %s' % (str(self._artifact_manager)))
    
    self.log_d('_resolve_packages: resolve_rv.resolved=%s' % (resolve_rv.resolved))
    self.log_d('_resolve_packages: resolve_rv.available=%s' % (resolve_rv.available))
    self.log_d('_resolve_packages: resolve_rv.latest=%s' % (resolve_rv.latest))
    self.log_d('_resolve_packages: resolve_rv.missing=%s' % (resolve_rv.missing))

    missing_packages = dependency_resolver.check_missing(resolve_rv.available.names(), requirements.names())
    if missing_packages:
      return self._resolve_result(resolve_rv.available, missing_packages, [])
    for pdesc in resolve_rv.resolved:
      self.log_d('_resolve_packages: RESOLVED: %s' % (pdesc.full_name))
    return self._resolve_result(resolve_rv.available, [], resolve_rv.resolved)

  def resolve_and_update_packages(self, project_name, requirements, build_target, options = None):
    check.check_string(project_name)
    check.check_requirement_list(requirements)
    check.check_build_target(build_target)
    check.check_venv_install_options(options, allow_none = True)

    resolve_rv = self._resolve_packages(build_target, requirements)
    if resolve_rv.missing:
      self.blurb('you lose again')
      self.blurb('missing artifacts at %s: %s' % (str(self._artifact_manager), ' '.join(resolve_rv.missing)))
      return []
    self._update_packages(project_name, resolve_rv.resolved, build_target, options)
    return resolve_rv.resolved

  def uninstall_packages(self, project_name, packages, build_target):
    check.check_string(project_name)
    check.check_package_descriptor_list(packages)
    check.check_build_target(build_target)
    self.log_i('uninstall_packages: project_name=%s; build_target=%s; packages=%s' % (project_name, build_target.build_path,
                                                                                      ','.join(packages.names())))

    # FIXME: no dependents handling
    pm = self._package_manager(project_name, build_target)
    pm.uninstall_packages(packages) #, build_target)
    return True

  def transform_env(self, env, project_name, build_target):
    check.check_dict(env)
    check.check_string(project_name)
    check.check_build_target(build_target)
    pm = self._package_manager(project_name, build_target)
    return pm.transform_env(env, pm.list_all_names())
  
  def bin_dir(self, project_name, build_target):
    check.check_string(project_name)
    check.check_build_target(build_target)
    pm = self._package_manager(project_name, build_target)
    return pm.bin_dir

  def tool_exe(self, project_name, build_target, tool_name):
    check.check_string(project_name)
    check.check_build_target(build_target)
    pm = self._package_manager(project_name, build_target)
    return pm.tool_exe(tool_name)

  def update_from_config(self, project_name, build_target, options = None):
    check.check_venv_install_options(options, allow_none = True)
    if not self._config.has_project(project_name):
      valid_project_names = self._config.project_names()
      self.blurb('invalid project \"%s\" - should be one of: %s' % (project_name, ' '.join(valid_project_names)), fit = True)
    return self._update_project_from_config(project_name, build_target, options)
  
  def _update_project_from_config(self, project_name, build_target, options):
    check.check_string(project_name)
    check.check_build_target(build_target)
    options = options or venv_install_options()
    pm = self._package_manager(project_name, build_target)
    self.log_i('_update_project_from_config: project_name=%s; build_target=%s; options=%s' % (project_name, build_target, options))
    if options.wipe_first:
      self._wipe_project_dir(project_name, build_target)
    
    requirements = self._config.packages(project_name, build_target)
    self.log_d('_update_project_from_config: requirements=%s' % (requirements))
    if not requirements:
      return self.clear_project_from_config(project_name, build_target)

    #all_artifacts = self._artifact_manager.list_all_by_package_descriptor(build_target)
    #self.log_d('_update_project_from_config: all_artifacts=%s' % ([ a.full_name for a in all_artifacts ]))

    #wanted_packages = self._package_descriptors_for_requirements(requirements, all_artifacts)
    #self.log_d('_update_project_from_config: wanted_packages=%s' % (wanted_packages))
    resolved_packages = self.resolve_and_update_packages(project_name, requirements, build_target, options)
    self.log_d('_update_project_from_config: resolved_packages=%s' % (resolved_packages))
    if not resolved_packages:
      self.blurb('failed to update %s from %s' % (project_name, self._config.filename))
      return False
    installed_packages = self.installed_packages(project_name, build_target)
    removed_packages_names = list(set(installed_packages.names()).difference(set(resolved_packages.names())))
    self.log_i('%s - installed packages: %s' % (project_name, ' '.join(installed_packages.names())))
    self.log_i('%s - removed packages: %s' % (project_name, ' '.join(removed_packages_names)))
    if removed_packages_names:
      self.uninstall_packages(project_name, pm.descriptors_for_names(removed_packages_names), build_target)
    if not options.dont_touch_scripts:
      self.save_system_setup_scripts(project_name, build_target)
    return True

  def _find_latest_version(clazz, req, descriptors):
    potential_matches = descriptors.filter_by_name(req.name)
    clazz.log_d('_find_latest_version: potential_matches=%s' % (potential_matches.names(include_version = True)))
    clazz.log_d('_find_latest_version: descriptors=%s' % (descriptors.names(include_version = True)))
    latest_pdesc = None
    for pd in potential_matches:
      if not latest_pdesc:
        latest_pdesc = pd
      else:
        if pd.version > latest_pdesc.version:
          latest_pdesc = pd
    return latest_pdesc
  
  def _find_matching_version(clazz, req, descriptors):
    potential_matches = descriptors.filter_by_name(req.name)
    latest_pdesc = None
    for pd in potential_matches:
      cmp_result = build_version.compare_upstream_version(req.version, str(pd.version))
      if cmp_result == 0:
        return pd
      if not latest_pdesc:
        latest_pdesc = pd
      else:
        if pd.version > latest_pdesc.version:
          latest_pdesc = pd
    return latest_pdesc

  def _package_descriptors_for_requirements(clazz, reqs, descriptors):
    result = package_descriptor_list()
    for req in reqs:
      if req.version:
        pd = clazz._find_matching_version(req, descriptors)
      else:
        pd = clazz._find_latest_version(req, descriptors)
      assert pd
      result.append(pd)
    return result
  
  def clear_project_from_config(self, project_name, build_target, options = None):
    options = options or venv_install_options()
    self.log_i('clear_project_from_config: project_name=%s; build_target=%s' % (project_name, build_target))
    installed_packages = self.installed_packages(project_name, build_target)
    self.uninstall_packages(project_name, installed_packages, build_target)
    if not options.dont_touch_scripts:
      self.save_system_setup_scripts(project_name, build_target)
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
  local _stuff_dir=${_root}/stuff
  local _env_dir=$_root/env
  source ${_env_dir}/framework/bes_shell.sh
  bes_env_path_prepend PATH ${_stuff_dir}/bin
  bes_env_path_prepend PYTHONPATH ${_stuff_dir}/lib/python
  bes_env_path_prepend PKG_CONFIG_PATH ${_stuff_dir}/lib/pkgconfig
  bes_env_path_prepend LD_LIBRARY_PATH ${_stuff_dir}/lib
  bes_env_path_prepend MANPATH ${_stuff_dir}/man
  bes_source_dir ${_env_dir}
}

_@NAME@_unsetup()
{
  local _root=${_@NAME@_root}
  local _stuff_dir=${_root}/stuff
  local _env_dir=$_root/env
  source ${_env_dir}/framework/bes_shell.sh
  bes_env_path_remove PATH ${_stuff_dir}/bin
  bes_env_path_remove PYTHONPATH ${_stuff_dir}/lib/python
  bes_env_path_remove PKG_CONFIG_PATH ${_stuff_dir}/lib/pkgconfig
  bes_env_path_remove LD_LIBRARY_PATH ${_stuff_dir}/lib
  bes_env_path_remove MANPATH ${_stuff_dir}/man
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

@NAME@_setup()
{
  local _root=${_@NAME@_root}
  source ${_root}/framework/bes_shell.sh
  local _system_path=$(bes_system_path)
  local _system_root=${_root}/${_system_path}
  local _stuff_dir=${_system_root}/stuff
  local _env_dir=${_system_root}/env
  bes_env_path_prepend PATH ${_stuff_dir}/bin
  bes_env_path_prepend PYTHONPATH ${_stuff_dir}/lib/python
  bes_env_path_prepend PKG_CONFIG_PATH ${_stuff_dir}/lib/pkgconfig
  bes_env_path_prepend LD_LIBRARY_PATH ${_stuff_dir}/lib
  bes_env_path_prepend MANPATH ${_stuff_dir}/man
  bes_source_dir ${_env_dir}
}

@NAME@_unsetup()
{
  local _root=${_@NAME@_root}
  source ${_root}/framework/bes_shell.sh
  local _system_path=$(bes_system_path)
  local _root=${_@NAME@_root}
  local _system_root=${_root}/${_system_path}
  local _stuff_dir=${_system_root}/stuff
  local _env_dir=${_system_root}/env
  bes_env_path_remove PATH ${_stuff_dir}/bin
  bes_env_path_remove PYTHONPATH ${_stuff_dir}/lib/python
  bes_env_path_remove PKG_CONFIG_PATH ${_stuff_dir}/lib/pkgconfig
  bes_env_path_remove LD_LIBRARY_PATH ${_stuff_dir}/lib
  bes_env_path_remove MANPATH ${_stuff_dir}/man
}
'''

  SYSTEM_RUN_SCRIPT_TEMPLATE = '''#!/bin/bash
source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/setup.sh"
@NAME@_setup
exec ${1+"$@"}
'''

  def save_system_setup_scripts(self, project_name, build_target):
    system_setup_script = venv_shell_script(self.SETUP_SYSTEM_SCRIPT_TEMPLATE, 'setup.sh')
    system_run_script = venv_shell_script(self.SYSTEM_RUN_SCRIPT_TEMPLATE, 'run.sh')
    setup_script = venv_shell_script(self.SETUP_SCRIPT_TEMPLATE, 'setup.sh')
    pm = self._package_manager(project_name, build_target)
    variables = {
      '@LIBRARY_PATH@': os_env.LD_LIBRARY_PATH_VAR_NAME,
      '@NAME@': project_name,
      '@SYSTEM@': build_target.system,
    }
    system_setup_script.save(pm.root_dir, variables)
    system_run_script.save(pm.root_dir, variables)
    parent_dir = path.join(self._root_dir, project_name)
    shell_framework.extract(path.join(parent_dir, 'framework'))
    setup_script.save(parent_dir, variables)
    system_run_script.save(parent_dir, variables)
  
  def _wipe_project_dir(self, project_name, build_target):
    project_root_dir = self._project_root_dir(project_name, build_target)
    self.blurb('wiping root dir: %s' % (project_root_dir))
    self.log_i('%s - wiping: %s' % (project_name, project_root_dir))
    file_util.remove(project_root_dir)
