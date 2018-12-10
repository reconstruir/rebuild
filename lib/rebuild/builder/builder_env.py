#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import file_trash
from bes.common import check
from bes.git import git_download_cache, git_util

from rebuild.tools_manager import tools_manager
from rebuild.checksum import checksum_manager
from rebuild.package import artifact_manager_chain, artifact_manager_local
from rebuild.base import build_blurb, package_descriptor, requirement_manager
from rebuild.storage import storage_factory
from rebuild.recipe import recipe_load_env
from rebuild.config import storage_config

from .builder_script_manager import builder_script_manager

class builder_env(object):

  def __init__(self, config, filenames):
    build_blurb.add_blurb(self, 'rebuild')
    self.config = config
    local_storage_dir = path.join(config.storage_cache_dir, 'local')
    self.storage_config = self._make_storage_config(config.storage_config, local_storage_dir, config.source_dir)
    self.storage = self._make_storage(self.storage_config,
                                      config.storage_provider,
                                      config.storage_cache_dir,
                                      config.no_network)
    self.blurb('storage: %s' % (self.storage))
    self.checksum_manager = self._make_checksum_manager(config.build_root)
    self.downloads_manager = self._make_downloads_manager(config.build_root)
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
  def _make_storage(clazz, config, provider, storage_cache_dir, no_network):
    download_credentials = config.get('download', provider)
    upload_credentials = config.get('upload', provider)
    local_storage_dir = path.join(storage_cache_dir, provider)
    factory_config = storage_factory.config(local_storage_dir, no_network, download_credentials, upload_credentials)
    return storage_factory.create(provider, factory_config)

  @classmethod
  def _make_checksum_manager(clazz, build_dir):
    return checksum_manager(path.join(build_dir, 'checksums'))

  @classmethod
  def _make_downloads_manager(clazz, build_dir):
    return git_download_cache(path.join(build_dir, 'downloads'))

  def reload_artifact_manager(self):
    self.artifact_manager = artifact_manager_chain()
    build_artifact_manager = artifact_manager_local(path.join(self.config.build_root, 'artifacts'))
    self.artifact_manager.add_artifact_manager(build_artifact_manager)
#    if self.config.artifacts_dir:
#      self.external_artifact_manager = artifact_manager_local(self.config.artifacts_dir)
#      self.external_artifact_manager.read_only = True
#      self.artifact_manager.add_artifact_manager(self.external_artifact_manager)
#    else:
    self.external_artifact_manager = None

  @classmethod
  def _make_storage_config(clazz, filename, root_dir, source_dir):
    if source_dir:
      return storage_config.make_local_config(None, source_dir)
    if not filename:
      return storage_config.make_local_config(None, root_dir)
    if not path.exists(filename):
      raise RuntimeError('artifacts config file not found: %s' % (filename))
    return storage_config.from_file(filename)
      
check.register_class(builder_env, include_seq = False)
