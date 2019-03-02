#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import file_trash
from bes.common import check
from bes.git import git_download_cache, git_util
from bes.properties.properties_editor import properties_editor

from rebuild.tools_manager import tools_manager
from rebuild.checksum import checksum_manager
from rebuild.package import artifact_manager_local
from rebuild.base import build_blurb, package_descriptor, requirement_manager
from rebuild.storage import storage_factory
from rebuild.recipe import recipe_load_env
from rebuild.config import storage_config_manager
from rebuild.package.artifact_manager_factory import artifact_manager_factory
from rebuild.source_ingester.http_download_cache import http_download_cache
from rebuild.recipe.variable_manager import variable_manager
from rebuild.storage.storage_artifactory import storage_artifactory

from .builder_script_manager import builder_script_manager
from .source_dir_zipball_cache import source_dir_zipball_cache

class builder_env(object):

  def __init__(self, config, filenames, checksum_getter, project_file_manager):
    build_blurb.add_blurb(self, 'rebuild')
    self.config = config
    self.checksum_getter = checksum_getter
    self.project_file_manager = project_file_manager
    self.storage_config_manager = self._load_storage_config_file(config.storage_config)
    self.sources_storage = self._make_storage(self.storage_config_manager,
                                              config.sources_config_name,
                                              'sources',
                                              config.storage_cache_dir,
                                              config.no_network)
    self.external_artifacts_storage = self._make_storage(self.storage_config_manager,
                                                         config.artifacts_config_name,
                                                         'artifacts',
                                                         config.storage_cache_dir,
                                                         config.no_network)
    self.blurb('sources_storage: %s' % (self.sources_storage))
    self.blurb('external_artifacts_storage: %s' % (self.external_artifacts_storage))
    self.checksum_manager = self._make_checksum_manager(config.build_root)
    self.git_downloads_manager = git_download_cache(path.join(config.build_root, 'downloads', 'git'))
    self.http_downloads_manager = http_download_cache(path.join(config.build_root, 'downloads', 'http'))
    self.source_dir_zipballs = source_dir_zipball_cache(path.join(config.build_root, 'downloads', 'source_dir_zipball'))
    self.reload_build_artifact_manager()
    self.external_artifact_manager = self._make_external_artifact_manager(self.external_artifacts_storage)
    self.requirements_artifact_manager = self.build_artifact_manager
    self.tools_manager = tools_manager(path.join(config.build_root, 'tools'),
                                       self.config.host_build_target,
                                       self.requirements_artifact_manager)
    self.properties = properties_editor.read_properties_file(config.properties_file)
    self.variable_manager = variable_manager()
    self.variable_manager.add_variables(config.project_file_variables)
    self.variable_manager.add_variables(self.properties)
      
    for key, value in config.cli_variables:
      self.variable_manager.add_variable(key, value)
      
    self.recipe_load_env = recipe_load_env(self)
    self.script_manager = builder_script_manager(filenames, self.config.build_target, self)
    self.requirement_manager = requirement_manager()
    self.trash = file_trash(self.config.trash_dir)
    for script in self.script_manager.scripts.values():
      self.requirement_manager.add_package(script.descriptor)
    self.imported_recipes = self.project_file_manager.imported_recipes(config.project_file,
                                                                       self.config.build_target)
  def recipe_is_imported(self, recipe_filename):
    return recipe_filename in self.imported_recipes

  def resolve_deps(self, descriptor, hardness, include_names):
    return self.requirement_manager.resolve_deps([descriptor.name], self.config.build_target.system, hardness, include_names)
  
  @classmethod
  def _make_storage(clazz, config_manager, config_name, sub_repo, storage_cache_dir, no_network):
    check.check_storage_config_manager(config_manager)
    check.check_string(config_name, allow_none = True)
    if not config_name:
      return None
    config = config_manager.get(config_name)
    if not config:
      raise RuntimeError('No storage config named \"%s\" found in: %s' % (config_name, config_manager.source))
    local_storage_dir = path.join(storage_cache_dir, config_name)
    factory_config = storage_factory.config(local_storage_dir, sub_repo, no_network, config)
    return storage_factory.create(factory_config)

  @classmethod
  def _make_checksum_manager(clazz, build_dir):
    return checksum_manager(path.join(build_dir, 'checksums'))

  def reload_build_artifact_manager(self):
    root_dir = path.join(self.config.build_root, 'artifacts')
    scm = storage_config_manager.make_local_config('builder_local', root_dir, None, None)
    config = scm.get('builder_local')
    factory_config = artifact_manager_factory.config(None, None, True, config)
    self.build_artifact_manager = artifact_manager_local(factory_config)

  def _make_external_artifact_manager(self, storage):
    if not storage:
      return None
    factory_config = artifact_manager_factory.config(storage._config.local_cache_dir,
                                                     None, False, storage._config.storage_config)
    return artifact_manager_factory.create(factory_config)
    root_dir = path.join(self.config.build_root, 'artifacts')
    scm = storage_config_manager.make_local_config('builder_local', root_dir, None, None)
    config = scm.get('builder_local')
    factory_config = artifact_manager_factory.config(None, None, True, config)
    self.build_artifact_manager = artifact_manager_local(factory_config)

  @classmethod
  def _load_storage_config_file(clazz, filename):
    filename = path.abspath(filename)
    if not path.exists(filename):
      raise RuntimeError('storage config file not found: %s' % (filename))
    return storage_config_manager.from_file(filename)

  @classmethod
  def print_properties(self):
    for key, value in sorted(self.properties.items()):
      print('%s: %s' % (key, value))
  
check.register_class(builder_env, include_seq = False)
