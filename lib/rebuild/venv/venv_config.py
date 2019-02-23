#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.common import check
from bes.text import string_list
from bes.fs import file_util
from bes.system import log

from rebuild.recipe import recipe_error
from rebuild.recipe.recipe_util import recipe_util

from .venv_project_config import venv_project_config
from .venv_config_parser import venv_config_parser

class venv_config(object):
  'Virtual environment configurations.  For now storage and projects.'

  def __init__(self, projects, storage_config, filename):
    check.check_storage_config_manager(storage_config)
    check.check_venv_project_config_list(projects)
    self._projects = projects
    self.storage_config = storage_config
    self.filename = filename
    self._project_map = {}
    for project in self._projects:
      self._project_map[project.name] = project

  def project_names(self):
    return sorted(self._project_map.keys())
    
  def projects(self):
    return sorted(self._project_map.keys())

  def has_project(self, project_name):
    return project_name in self._project_map

  def package_names(self, project_name, build_target):
    return self.packages(project_name, build_target).names()
  
  def packages(self, project_name, build_target):
    assert self.has_project(project_name)
    return self._project_map[project_name].resolve_packages(build_target.system)
  
  @classmethod
  def load(clazz, filename, build_target):
    clazz.log_i('loading config: %s for %s' % (filename, build_target.build_path))
    check.check_string(filename)
    check.check_build_target(build_target)
    if not path.isfile(filename):
      raise RuntimeError('venv config file not found: %s' % (filename))
    if venv_project_config.is_venv_config(filename):
      text = file_util.read(filename, codec = 'utf8')
      parser = venv_config_parser(filename, text)
      projects, storage_config = parser.parse()
      return venv_config(projects, storage_config, filename)
    else:
      raise RuntimeError('Not a valid venv config file: %s' % (filename))
    
log.add_logging(venv_config, 'venv')
check.register_class(venv_config)
