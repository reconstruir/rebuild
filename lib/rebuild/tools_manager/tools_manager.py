#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.system import host, os_env, os_env_var
from bes.fs import file_util
from rebuild.base import build_target, build_system, package_descriptor
from rebuild.package import artifact_manager
from .build_requirement_manager import build_requirement_manager

class tools_manager(object):

  def __init__(self, tools_dir):
    assert tools_dir
    tools_dir = path.abspath(tools_dir)
    self.tools_dir = path.join(tools_dir, host.SYSTEM)
    self.package_manager = build_requirement_manager(self.tools_dir)

  def update(self, packages, am):
    check.check_package_descriptor_seq(packages)
    assert isinstance(am, artifact_manager)
    self.package_manager.install_packages(packages, am)
    bin_dirs = self.all_bin_dirs(packages)
    os_env.PATH.prepend(bin_dirs)

  def uninstall(self, package_name):
    assert False
    
  def tool_exe(self, package_info, tool_name):
    'Return an abs path to the given tool.'
    return self.package_manager.tool_exe(package_info, tool_name)

  def bin_dirs(self, package_names):
    return self.package_manager.bin_dirs(package_names)

  # FIXME: whats the difference between bin_dirs and all_bin_dirs
  def all_bin_dirs(self, packages):
    return [ self.package_manager.bin_dir(p) for p in packages ]

  def all_lib_dirs(self, packages):
    return [ self.package_manager.lib_dir(p) for p in packages ]

  def all_env_vars(self, packages):
    return self.package_manager.all_env_vars(packages)

  def shell_env(self, packages):
    tools_bin_path = [ self.package_manager.bin_dir(p) for p in packages ]
    tools_lib_path = [ self.package_manager.lib_dir(p) for p in packages ]
    env = {
      os_env.LD_LIBRARY_PATH_VAR_NAME: os_env_var.path_join(tools_lib_path),
      'PATH': os_env_var.path_join(tools_bin_path),
      'PYTHONPATH': os_env_var.path_join(self.package_manager.python_lib_dirs(packages)),
    }
    all_env_vars = self.package_manager.all_env_vars(packages)
    os_env.update(env, all_env_vars)
    return env

  def export_variables_to_current_env(self, packages):
    all_env_vars = self.package_manager.all_env_vars(packages)
    for key, value in all_env_vars.items():
      os_env_var(key).value = value
