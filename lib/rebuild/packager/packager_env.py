#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import time_util
from bes.fs import file_util
from rebuild.package_manager import package_manager

class packager_env(object):

  def __init__(self, script, rebuild_env, all_scripts):
    self.rebuild_env = rebuild_env
    self.script = script
    self.all_scripts = all_scripts
    self.working_dir = self._make_working_dir(rebuild_env.config.build_root)
    self.source_unpacked_dir = path.join(self.working_dir, 'source')
    self.build_dir = path.join(self.working_dir, 'build')
    self.stage_dir = path.join(self.working_dir, 'stage')
    self.artifact_stage_dir = path.join(self.working_dir, 'artifact')
    self.logs_dir = path.join(self.working_dir, 'logs')
    self.test_dir = path.join(self.working_dir, 'test')
    self.check_dir = path.join(self.working_dir, 'check')
    self.requirements_manager = package_manager(path.join(self.working_dir, 'requirements'))
    self.sources = []
    self.targets = []
    self.stage_lib_dir = path.join(self.stage_dir, 'lib')
    self.stage_bin_dir = path.join(self.stage_dir, 'bin')
    self.stage_compile_instructions_dir = path.join(self.stage_lib_dir, 'rebuild_instructions')

  def _make_working_dir(self, build_dir):
    base_dir = '%s_%s' % (self.script.package_descriptor.full_name, time_util.timestamp())
    working_dir = path.join(build_dir, base_dir)
    file_util.mkdir(working_dir)
    return working_dir
