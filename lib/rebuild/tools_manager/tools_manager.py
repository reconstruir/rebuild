#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path, os
from bes.common import check, object_util
from bes.system import execute, os_env
from rebuild.base import build_target, build_level, package_descriptor_list
from rebuild.venv.venv_manager import venv_manager
from bes.debug import debug_timer

class tools_manager(object):

  def __init__(self, root_dir, build_target, artifact_manager):
    check.check_string(root_dir)
    check.check_build_target(build_target)
    check.check_artifact_manager(artifact_manager)
    self._build_target = build_target
    self._root_dir = root_dir
    self._artifact_manager = artifact_manager
    self._timer = debug_timer('am', 'error', disabled = True)
    self._manager = venv_manager(None, self._artifact_manager, self._build_target, self._root_dir)
    
  @property
  def root_dir(self):
    return self._root_dir
    
  def ensure_tools(self, packages):
    packages = self._resolve_packages(packages)
    check.check_package_descriptor_list(packages)
    for pkg_desc in packages:
      self._ensure_one_tool(pkg_desc)

  def _ensure_one_tool(self, pkg_desc):
    check.check_package_descriptor(pkg_desc)
    # If we created this tool dir before were done.  There is no possible update
    # Update of tools requires a change in the version or revision.
    if path.exists(self._package_root_dir(pkg_desc)):
      return
    # Figure out the dependencies for this tool
    packages = package_descriptor_list([ pkg_desc ])
    #requrements = package_descriptor_list([ pkg_desc ]).to_requirement_list()
    resolved_tools = self._resolve_tools_deps(packages)
    for tool_pkg_desc in resolved_tools:
      project_name = tool_pkg_desc.full_name
      self._timer.start('%s: resolve_and_update_packages' % (project_name))
      self._manager.resolve_and_update_packages(project_name,
                                                package_descriptor_list([ tool_pkg_desc ]).to_requirement_list(),
                                                self._build_target)
      self._timer.stop()
      self._manager.save_system_setup_scripts(project_name, self._build_target)

  def _poto_resolve_tools_deps(self, requirements):
    check.check_requirement_list(requirements)
    return self._artifact_manager.poto_resolve_deps(requirements, self._build_target, [ 'TOOL' ], True)

  def _resolve_tools_deps(self, packages):
    check.check_package_descriptor_list(packages)
    return self._artifact_manager.resolve_deps(packages.names(), self._build_target, [ 'TOOL' ], True)

  @classmethod
  def _resolve_packages(clazz, packages):
    if check.is_package_descriptor(packages):
      return package_descriptor_list([ packages ])
    elif check.is_package_descriptor_list(packages):
      return packages
    else:
      raise TypeError('Invalid packages: %s - %s' % (packages, type(packages)))
    
  def transform_env(self, env, packages):
    check.check_dict(env)
    packages = self._resolve_packages(packages)
    check.check_package_descriptor_list(packages)
    resolved_tools = self._resolve_tools_deps(packages)
    transformed_env = copy.deepcopy(env)
    for tool in resolved_tools:
      project_name = tool.full_name
      transformed_env = self._manager.transform_env(transformed_env, project_name, self._build_target)
    return transformed_env

  def expose_env(self, pkg_descs):
    old_env = os_env.clone_current_env()
    new_env = self.transform_env(old_env, pkg_descs)
    for key, value in new_env.items():
      os.environ[key] = value
  
  def _package_root_dir(self, pkg_desc):
    return path.join(self._root_dir, pkg_desc.full_name)
  
  def run_tool(self, pkg_descs, command, env, *args):
    if env is None:
      env = os_env.clone_current_env()
    else:
      check.check_dict(env)
    env = self.transform_env(env, pkg_descs)
    if 'env' in args:
      env.update(args['env'])
      del args['env']
    return execute.execute(command, env = env, *args)
