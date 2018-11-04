#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.fs import file_trash
from bes.common import check
from bes.git import git_download_cache, git_util

from rebuild.tools_manager import tools_manager
from rebuild.checksum import checksum_manager
from rebuild.package import artifact_manager_chain, artifact_manager_local
from rebuild.base import build_blurb, package_descriptor, requirement_manager
from rebuild.source_finder import source_finder_git_repo, source_finder_local, source_finder_pcloud, source_finder_chain
from rebuild.recipe import recipe_load_env
from rebuild.pcloud import pcloud_credentials

from .builder_script_manager import builder_script_manager

class builder_env(object):

  def __init__(self, config, filenames):
    build_blurb.add_blurb(self, 'rebuild')
    self.config = config
    self.source_finder = self._make_source_finder(config.build_root,
                                                  config.source_dir,
                                                  config.source_git,
                                                  config.source_pcloud,
                                                  config.no_network)
    self.blurb('source_finder: %s' % (self.source_finder))
    self.checksum_manager = self._make_checksum_manager(config.build_root)
    self.tools_manager = self._make_tools_manager(config.build_root)
    self.downloads_manager = self._make_downloads_manager(config.build_root)
    self.reload_artifact_manager()
    self.recipe_load_env = recipe_load_env(self)
    self.script_manager = builder_script_manager(filenames, self.config.build_target, self)
    self.requirement_manager = requirement_manager()
    self.trash = file_trash(self.config.trash_dir)
    for script in self.script_manager.scripts.values():
      self.requirement_manager.add_package(script.descriptor)
      
  def resolve_deps(self, descriptor, hardness, include_names):
    return self.requirement_manager.resolve_deps([descriptor.name], self.config.build_target.system, hardness, include_names)
  
  @classmethod
  def _make_source_finder(clazz, build_dir, source_dir, source_git, source_pcloud, no_network):
    chain = source_finder_chain()
    if source_dir:
      finder = source_finder_local(source_dir)
      chain.add_finder(finder)
    if source_git:
      root = path.join(build_dir, 'third_party_tarballs', git_util.sanitize_address(source_git))
      finder = source_finder_git_repo(root, source_git, no_network = no_network, update_only_once = True)
      chain.add_finder(finder)
    if source_pcloud:
      credentials = pcloud_credentials.from_file(source_pcloud)
      if not credentials.is_valid():
        raise RuntimeError('Invalid pcloud credentials: %s' % (source_pcloud))
      root = path.join(build_dir, 'downloads', 'pcloud')
      finder = source_finder_pcloud(root, credentials, no_network = no_network)
      chain.add_finder(finder)
    if len(chain) == 0:
        raise RuntimeError('No valid source finders given.')
    return chain

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
    if self.config.artifacts_dir:
      self.external_artifact_manager = artifact_manager_local(self.config.artifacts_dir)
      self.external_artifact_manager.read_only = True
      self.artifact_manager.add_artifact_manager(self.external_artifact_manager)
    else:
      self.external_artifact_manager = None
      
  def _make_tools_manager(self, build_dir):
    return tools_manager(path.join(build_dir, 'tools'), self.config.host_build_target)

  def update_tools(self, packages):
    check.check_package_descriptor_seq(packages)
    self.tools_manager.update(packages, self.artifact_manager)

check.register_class(builder_env, include_seq = False)
