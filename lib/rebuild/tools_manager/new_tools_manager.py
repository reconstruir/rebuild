#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, string_util
from bes.system import host, os_env, os_env_var
from rebuild.base import build_target, build_level
from rebuild.package import package_manager
from rebuild.manager import manager
from bes.debug import debug_timer

class new_tools_manager(object):

  def __init__(self, root_dir, artifact_manager):
    check.check_string(root_dir)
    check.check_artifact_manager(artifact_manager)
    self._build_target = build_target.make_host_build_target()
    self._root_dir = root_dir
    self._artifact_manager = artifact_manager
    self._timer = debug_timer('tm', level = 'error')
    self._manager = manager(self._artifact_manager, self._build_target, root_dir = self._root_dir)
    
  @property
  def root_dir(self):
    return self._root_dir
    
  def ensure_tools(self, packages):
    check.check_package_descriptor_seq(packages)
    for package in packages:
      self.ensure_tool(package)

  @classmethod
  def _make_package_name(clazz, pkg_desc):
    return string_util.replace_punctuation(pkg_desc.full_name, '_')

  def ensure_tool(self, pkg_desc):
    check.check_package_descriptor(pkg_desc)
    if path.exists(self._package_root_dir(pkg_desc)):
      return
    self._timer.start('%s: ensure_tool()' % (pkg_desc.full_name))
    project_name = self._make_package_name(pkg_desc)
    self._timer.start('%s: resolve_and_update_packages' % (project_name))
    self._manager.resolve_and_update_packages(project_name,
                                              [ pkg_desc.name ],
                                              self._build_target,
                                              allow_downgrade = False,
                                              force_install = False)
    self._manager._save_system_setup_scripts(project_name, self._build_target)
    self._timer.stop()

  def transform_env(self, pkg_desc, env):
    project_name = self._make_package_name(pkg_desc)
    return self._manager.transform_env(env, project_name, self._build_target)

  def _package_root_dir(self, pkg_desc):
    return path.join(self._root_dir, self._make_package_name(pkg_desc))

  def environment(self, tools):
    self._timer.start('%s: _get_manager()' % (pkg_desc.full_name))
    root_dir = self._package_root_dir(pkg_desc)
    if root_dir not in self._package_managers:
      self._package_managers[root_dir] = package_manager(root_dir, self._artifact_manager)
    self._timer.stop()
    return self._package_managers[root_dir]
  
  def _all_bin_dirs(self, packages):
    return [ self.package_manager.bin_dir(p) for p in packages ]

  def _all_lib_dirs(self, packages):
    return [ self.package_manager.lib_dir(p) for p in packages ]

  def _all_python_lib_dirs(self, packages):
    return [ self.package_manager.python_lib_dir(p) for p in packages ]
  
  def shell_env(self, packages):
    tools_bin_path = self._all_bin_dirs(packages)
    tools_lib_path = self._all_lib_dirs(packages)
    tools_python_lib_path = self._all_python_lib_dirs(packages)
    env = {
      os_env.LD_LIBRARY_PATH_VAR_NAME: os_env_var.path_join(tools_lib_path),
      'PATH': os_env_var.path_join(tools_bin_path),
      'PYTHONPATH': os_env_var.path_join(tools_python_lib_path),
    }
    all_env_vars = self.package_manager.all_env_vars(packages)
    os_env.update(env, all_env_vars)
    return env

  def export_variables_to_current_env(self, packages):
    all_env_vars = self.package_manager.all_env_vars(packages)
    for key, value in all_env_vars.items():
      os_env_var(key).value = value
