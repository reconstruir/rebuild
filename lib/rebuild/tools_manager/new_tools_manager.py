#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, object_util, string_util
from bes.system import execute, host, os_env, os_env_var
from rebuild.base import build_target, build_level, package_descriptor_list
from rebuild.manager import manager
from bes.debug import debug_timer, noop_debug_timer

class new_tools_manager(object):

  def __init__(self, root_dir, build_target, artifact_manager):
    check.check_string(root_dir)
    check.check_build_target(build_target)
    check.check_artifact_manager(artifact_manager)
    self._build_target = build_target
    self._root_dir = root_dir
    self._artifact_manager = artifact_manager
    #self._timer = debug_timer('tm', level = 'error')
    self._timer = noop_debug_timer('am', 'error')
    self._manager = manager(self._artifact_manager, self._build_target, root_dir = self._root_dir)
    
  @property
  def root_dir(self):
    return self._root_dir
    
  def ensure_tools(self, pkg_descs):
    pkg_descs = package_descriptor_list.resolve(pkg_descs)
    for package in pkg_descs:
      self._ensure_one_tool(package)

  @classmethod
  def _make_package_name(clazz, pkg_desc):
    return string_util.replace_punctuation(pkg_desc.full_name, '_')

  def _ensure_one_tool(self, pkg_desc):
    check.check_package_descriptor(pkg_desc)
    # If we created this tool dir before were done.  There is no possible update
    # Update of tools requires a change in the version or revision.
    if path.exists(self._package_root_dir(pkg_desc)):
      return
    # Figure out the dependencies for this tool
    resolved_tools = self._resolve_tools_deps(package_descriptor_list([pkg_desc]))
    for tool in resolved_tools:
      project_name = self._make_package_name(tool)
      self._timer.start('%s: resolve_and_update_packages' % (project_name))
      self._manager.resolve_and_update_packages(project_name,
                                                [ tool.name ],
                                                self._build_target,
                                                allow_downgrade = False,
                                                force_install = False)
      self._timer.stop()
      self._manager.save_system_setup_scripts(project_name, self._build_target)

  def _resolve_tools_deps(self, pkg_descs):
    check.check_package_descriptor_list(pkg_descs)
    return self._artifact_manager.resolve_deps(pkg_descs.names(), self._build_target, [ 'TOOL' ], True)

  def transform_env(self, pkg_descs, env):
    pkg_descs = package_descriptor_list.resolve(pkg_descs)
    resolved_tools = self._resolve_tools_deps(pkg_descs)
    env = {}
    for tool in resolved_tools:
      project_name = self._make_package_name(tool)
      env = self._manager.transform_env(env, project_name, self._build_target)
    return env
    
  def _transform_one_env(self, pkg_desc, env):
    project_name = self._make_package_name(pkg_desc)
    return self._manager.transform_env(env, project_name, self._build_target)
  
  def _package_root_dir(self, pkg_desc):
    return path.join(self._root_dir, self._make_package_name(pkg_desc))
  
  def shell_env(self, pkg_descs):
    pkg_descs = package_descriptor_list.resolve(pkg_descs)
    return self.transform_env(pkg_descs, os_env.clone_current_env())

  def export_variables_to_current_env(self, pkg_descs):
    pkg_descs = package_descriptor_list.resolve(pkg_descs)
    for key, value in self.shell_env(pkg_descs):
      os_env_var(key).value = value

  def run_tool(self, pkg_descs, command, *args):
    pkg_descs = package_descriptor_list.resolve(pkg_descs)
    env = self.transform_env(pkg_descs, os_env.clone_current_env())
    if 'env' in args:
      env.update(args['env'])
      del args['env']
    for k, v in env.items():
      print('ENV: %s=%s' % (k, v))
    return execute.execute(command, env = env, *args)
