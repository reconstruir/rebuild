#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import time_util
from bes.fs import file_util, temp_file
from bes.git import git_download_cache
from rebuild.package_manager import artifact_manager, package_manager
from rebuild import package_descriptor, requirement

from .rebuild_manager import rebuild_manager

class packager_env(object):

  THIRD_PARTY_PREFIX = 'rebbe_'

  def __init__(self,
               script,
               all_scripts,
               tmp_dir,
               publish_dir,
               working_dir = None,
               rebbe_root = None,
               downloads_root = None,
               third_party_sources_root = None):
    assert tmp_dir
    
    self.script = script
    self.all_scripts = all_scripts
    self.build_target = script.build_target
    if working_dir:
      self.working_dir = working_dir
    else:
      self.working_dir = self.__make_tmp_working_dir(tmp_dir)
    self.source_unpacked_dir = path.join(self.working_dir, 'source')
    self.build_dir = path.join(self.working_dir, 'build')
    self.stage_dir = path.join(self.working_dir, 'stage')
    self.artifact_stage_dir = path.join(self.working_dir, 'artifact')
    self.logs_dir = path.join(self.working_dir, 'logs')
    self.test_dir = path.join(self.working_dir, 'test')
    self.check_dir = path.join(self.working_dir, 'check')
    self.tmp_dir = path.join(self.working_dir, 'tmp')
    self.download_dir = path.join(self.working_dir, 'download')
    self.artifact_manager = artifact_manager(publish_dir, no_git = True)
    self.requirements_manager = package_manager(path.join(self.working_dir, 'requirements'))
    self.rebbe = rebuild_manager(rebbe_root, self.artifact_manager)
    self.downloads = git_download_cache(downloads_root)
    self.third_party_sources_root = third_party_sources_root
    self.sources = []
    self.targets = []
    self.stage_lib_dir = path.join(self.stage_dir, 'lib')
    self.stage_bin_dir = path.join(self.stage_dir, 'bin')
    self.stage_compile_instructions_dir = path.join(self.stage_lib_dir, 'rebuild_instructions')
    
  @property
  def source_dir(self):
    return self.script.source_dir

  @property
  def package_descriptor(self):
    return self.script.package_info

  def __make_tmp_working_dir(self, tmp_dir):
    assert tmp_dir
    base_dir = '%s_%s' % (self.script.package_info.full_name, time_util.timestamp())
    working_dir = path.join(tmp_dir, base_dir)
    file_util.mkdir(working_dir)
    return working_dir

  @property
  def checksum_dir(self):
    return self.rebbe.checksum_dir(self.script.package_info, self.build_target)
