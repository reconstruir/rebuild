#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

from rebuild.base import build_target
from rebuild.venv.venv_config import venv_config
from rebuild.venv.venv_manager import venv_manager
from rebuild.recipe.variable_manager import variable_manager

from _rebuild_testing.artifact_manager_tester import artifact_manager_tester

class venv_tester(object):

  _STORAGE_CONFIG_TEMPLATE = '''\
!rebuild.revenv!
config
  storage
    name: unit_test_storage
    provider: local
    location: {artifacts_dir}
'''

  def __init__(self, config, recipes = None, debug = False, vmanager = None):
    self.variable_manager = vmanager or variable_manager()
    self.tmp_dir = self._make_temp_dir(debug)
    self.amt = artifact_manager_tester(recipes = recipes)
    if recipes:
      self.amt.publish(recipes)
    self.config_filename = path.join(self.tmp_dir, 'config.revenv')
    self._write_config_file(self.config_filename, config, self.amt.am)
    self.build_target = build_target.parse_path('linux-ubuntu-18/x86_64/release')
    config_obj = venv_config.load(self.config_filename, self.build_target, self.variable_manager)
    self.manager = venv_manager(config_obj, self.amt.am, self.build_target, self.tmp_dir)
  
  @classmethod
  def _make_temp_dir(clazz, debug):
    tmp_dir = temp_file.make_temp_dir(delete = not debug)
    if debug:
      print("tmp_dir: ", tmp_dir)
    return tmp_dir

  @classmethod
  def _write_config_file(clazz, filename, config, artifact_manager):
    storage_content = clazz._STORAGE_CONFIG_TEMPLATE.format(artifacts_dir = artifact_manager._root_dir)
    content = config.format(head = storage_content)
    file_util.save(filename, content = content)
  
  def installed_packages(self, project_name, include_version = False):
    return self.manager.installed_packages_names(project_name, self.build_target, include_version = include_version)

  def update_from_config(self, project_name, options = None):
    return self.manager.update_from_config(project_name, self.build_target, options = options)

  def clear_project_from_config(self, project_name):
    return self.manager.clear_project_from_config(project_name, self.build_target)

  def rewrite_config(self, config):
    self._write_config_file(self.config_filename, config, self.amt.am)
    config_obj = venv_config.load(self.config_filename, self.build_target, self.variable_manager)
    self.manager._config = config_obj

  def publish_artifacts(self, adescs, mutations = {}):
    self.amt.publish(adescs, mutations = mutations)
    
  def add_recipes(self, recipes):
    self.amt.add_recipes(recipes)
    
  def clear_artifacts(self):
    self.amt.retire_all()

  def transform_env(self, env, project_name, build_target):
    return self.manager.transform_env(env, project_name, build_target)
