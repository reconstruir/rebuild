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

class rebuild_env(object):

  def __init__(self, root_dir, config):
    self.config = config
    self.source_finder = self._make_source_finder(root_dir, config.source_dir, config.third_party_address, config.no_network)
    self.checksum_manager = self._make_checksum_manager(root_dir)
    self.tools_manager = self._make_tools_manager(root_dir)
    self.downloads_manager = self._make_downloads_manager(root_dir)
    self.artifact_manager = self._make_artifact_manager(root_dir)
      
  @classmethod
  def _make_source_finder(clazz, tmp_dir, source_dir, address, no_network):
    chain = source_finder_chain()
    if source_dir:
     chain.add_finder(local_source_finder(source_dir))
    else:
     root = path.join(tmp_dir, 'third_party_sources', git_util.sanitize_address(address))
     chain.add_finder(repo_source_finder(root, address, no_network = no_network, update_only_once = True))
    return chain

  @classmethod
  def _make_checksum_manager(clazz, tmp_dir):
    return checksum_manager(path.join(tmp_dir, 'checksums'))

  @classmethod
  def _make_downloads_manager(clazz, tmp_dir):
    return git_download_cache(path.join(tmp_dir, 'downloads'))
  
  @classmethod
  def _make_artifact_manager(clazz, tmp_dir):
    return artifact_manager(path.join(tmp_dir, 'artifacts'), no_git = True)

  @classmethod
  def _make_tools_manager(clazz, tmp_dir):
    return tools_manager(path.join(tmp_dir, 'tools'))

  def update_tools(self, packages):
    assert package_descriptor.is_package_info_list(packages)
    self.tools_manager.update(packages, self.artifact_manager)

  def tool_exe(self, package_info, tool_name):
    'Return an abs path to the given tool.'
    return self.tools_manager.tool_exe(package_info, tool_name)
    
