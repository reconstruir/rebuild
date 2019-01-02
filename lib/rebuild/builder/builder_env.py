#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import file_trash
from bes.common import check
from bes.git import git_download_cache, git_util

from rebuild.tools_manager import tools_manager
from rebuild.checksum import checksum_manager
from rebuild.package import artifact_manager_local
from rebuild.base import build_blurb, package_descriptor, requirement_manager
from rebuild.storage import storage_factory
from rebuild.recipe import recipe_load_env
from rebuild.config import storage_config_manager
from rebuild.source_ingester.http_download_cache import http_download_cache

from .builder_script_manager import builder_script_manager

class builder_env(object):

  def __init__(self, config, filenames):
    build_blurb.add_blurb(self, 'rebuild')
    self.config = config
    local_storage_cache_dir = path.join(config.storage_cache_dir, 'local')
    self.storage_config_manager = self._load_storage_config_file(config.storage_config)
    self.sources_storage = self._make_storage(self.storage_config_manager,
                                              config.sources_config_name,
                                              'sources',
                                              config.storage_cache_dir,
                                              config.no_network)
    self.blurb('sources_storage: %s' % (self.sources_storage))
    self.checksum_manager = self._make_checksum_manager(config.build_root)
    self.git_downloads_manager = git_download_cache(path.join(config.build_root, 'downloads', 'git'))
    self.http_downloads_manager = http_download_cache(path.join(config.build_root, 'downloads', 'http'))
    self.reload_artifact_manager()
    self.tools_manager = tools_manager(path.join(config.build_root, 'tools'),
                                       self.config.host_build_target,
                                       self.artifact_manager)
    self.recipe_load_env = recipe_load_env(self)
    self.script_manager = builder_script_manager(filenames, self.config.build_target, self)
    self.requirement_manager = requirement_manager()
    self.trash = file_trash(self.config.trash_dir)
    for script in self.script_manager.scripts.values():
      self.requirement_manager.add_package(script.descriptor)

  def resolve_deps(self, descriptor, hardness, include_names):
    return self.requirement_manager.resolve_deps([descriptor.name], self.config.build_target.system, hardness, include_names)
  
  @classmethod
  def _make_storage(clazz, config_manager, config_name, sub_repo, storage_cache_dir, no_network):
    check.check_storage_config_manager(config_manager)
    config = config_manager.get(config_name)
    if not config:
      raise RuntimeError('No storage config named \"%s\" found in: %s' % (config_name, config_manager.source))

    #return clazz.__bases__[0].__new__(clazz, name, provider, location, repo, root_dir, download, upload)    
    
    #download_credentials = config.get('download', provider)
    #upload_credentials = config.get('upload', provider)
    local_storage_dir = path.join(storage_cache_dir, config.provider)
    factory_config = storage_factory.config(local_storage_dir, sub_repo, no_network, config)
    return storage_factory.create(factory_config)

  @classmethod
  def _make_checksum_manager(clazz, build_dir):
    return checksum_manager(path.join(build_dir, 'checksums'))

  def reload_artifact_manager(self):
    self.artifact_manager = artifact_manager_local(path.join(self.config.build_root, 'artifacts'))
    self.external_artifact_manager = None

  @classmethod
  def _load_storage_config_file(clazz, filename):
    if not path.exists(filename):
      raise RuntimeError('storage config file not found: %s' % (filename))
    return storage_config_manager.from_file(filename)
      
check.register_class(builder_env, include_seq = False)
