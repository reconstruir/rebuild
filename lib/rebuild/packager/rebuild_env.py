#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from rebuild.packager import rebuild_manager
from rebuild.package_manager import artifact_manager
from rebuild.tools_manager import tools_manager
from rebuild.checksum import checksum_manager
from rebuild.package_manager import artifact_manager
from rebuild import package_descriptor
from bes.git import git_download_cache, git_util
from rebuild.source_finder import repo_source_finder, local_source_finder, source_finder_chain
from .build_script_manager import build_script_manager

class rebuild_env(object):

  def __init__(self, config, filenames):
    self.config = config
    # FIXME: move this to config
    self.config.builds_dir = path.join(config.build_root, 'builds', self.config.build_target.build_path)
    self.source_finder = self._make_source_finder(config.build_root, config.source_dir, config.third_party_address, config.no_network)
    self.checksum_manager = self._make_checksum_manager(config.build_root)
    self.tools_manager = self._make_tools_manager(config.build_root)
    self.downloads_manager = self._make_downloads_manager(config.build_root)
    self.artifact_manager = self._make_artifact_manager(config.build_root)
    self.script_manager = build_script_manager(filenames, config.build_target, self.config.builds_dir)
    
  @classmethod
  def _make_source_finder(clazz, build_dir, source_dir, address, no_network):
    chain = source_finder_chain()
    if source_dir:
     chain.add_finder(local_source_finder(source_dir))
    else:
     root = path.join(build_dir, 'third_party_sources', git_util.sanitize_address(address))
     chain.add_finder(repo_source_finder(root, address, no_network = no_network, update_only_once = True))
    return chain

  @classmethod
  def _make_checksum_manager(clazz, build_dir):
    return checksum_manager(path.join(build_dir, 'checksums'))

  @classmethod
  def _make_downloads_manager(clazz, build_dir):
    return git_download_cache(path.join(build_dir, 'downloads'))
  
  @classmethod
  def _make_artifact_manager(clazz, build_dir):
    return artifact_manager(path.join(build_dir, 'artifacts'), no_git = True)

  @classmethod
  def _make_tools_manager(clazz, build_dir):
    return tools_manager(path.join(build_dir, 'tools'))

  def update_tools(self, packages):
    assert package_descriptor.is_package_info_list(packages)
    self.tools_manager.update(packages, self.artifact_manager)

  def tool_exe(self, package_info, tool_name):
    'Return an abs path to the given tool.'
    return self.tools_manager.tool_exe(package_info, tool_name)
    
