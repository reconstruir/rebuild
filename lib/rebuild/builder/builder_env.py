#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

from bes.common import check
from rebuild.package import artifact_manager
from rebuild.tools_manager import tools_manager
from rebuild.checksum import checksum_manager
from rebuild.package import artifact_manager
from rebuild.base import package_descriptor, requirement_manager
from bes.git import git_download_cache, git_util
from rebuild.source_finder import repo_source_finder, local_source_finder, source_finder_chain
from .builder_script_manager import builder_script_manager

class builder_env(object):

  def __init__(self, config, filenames):
    self.config = config
    self.source_finder = self._make_source_finder(config.build_root, config.source_dir, config.third_party_address, config.no_network)
    self.checksum_manager = self._make_checksum_manager(config.build_root)
    self.tools_manager = self._make_tools_manager(config.build_root)
    self.downloads_manager = self._make_downloads_manager(config.build_root)
    self.artifact_manager = self._make_artifact_manager(config.build_root)
    self.script_manager = builder_script_manager(filenames, self)
    self.requirement_manager = requirement_manager()
    for script in self.script_manager.scripts.values():
      self.requirement_manager.add_package(script.descriptor)
      
  def resolve_deps_caca_tool(self, descriptor, include_names):
    return self.requirement_manager.resolve_deps_caca_tool([descriptor.name], self.config.host_build_target.system, include_names)
      
  def resolve_deps_poto_build_run(self, descriptor, include_names):
    return self.requirement_manager.resolve_deps_poto_build_run([descriptor.name], self.config.build_target.system, include_names)

  def resolve_deps_poto_run(self, descriptor, include_names):
    return self.requirement_manager.resolve_deps_poto_run([descriptor.name], self.config.build_target.system, include_names)
  
  def resolve_deps(self, descriptor, hardness, include_names):
    return self.requirement_manager.resolve_deps_poto([descriptor.name], self.config.build_target.system, hardness, include_names)
  
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
    check.check_package_descriptor_seq(packages)
    self.tools_manager.update(packages, self.artifact_manager)

  def tool_exe(self, package_info, tool_name):
    'Return an abs path to the given tool.'
    return self.tools_manager.tool_exe(package_info, tool_name)
    
