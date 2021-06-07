#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple
from bes.build.build_arch import build_arch
from bes.build.build_level import build_level
from bes.build.build_system import build_system
from bes.build.build_target import build_target
from bes.common.time_util import time_util
from bes.debug.debug_timer import debug_timer
from bes.system.log import log
from bes.key_value.key_value_list import key_value_list

class builder_config(object):

  DEFAULT_THIRD_PARTY_PREFIX = 'rebbe_'
  DEFAULT_PYTHON_VERSION = '2.7'
  #DEFAULT_PYTHON_VERSION = '3.7'
  
  def __init__(self):
    self._build_root = None
    self.build_target = build_target.make_host_build_target(level = build_level.RELEASE)
    self.host_build_target = build_target.make_host_build_target(level = build_level.RELEASE)
    self.root_dir = None
    self.deps_only = False
    self.disabled = False
    self.keep_going = False
    self.no_checksums = False
    self.no_network = False
    self.recipes_only = False
    self.scratch = False
    self.no_tests = False
    self.skip_to_step = None
    self.third_party_prefix = self.DEFAULT_THIRD_PARTY_PREFIX
    self.timestamp = time_util.timestamp()
    self.tmp_dir = None
    self.tools_only = False
    self.users = False
    self.verbose = False
    self.wipe = False
    self._performance = False
    self.timer = debug_timer('perf', 'debug', disabled = False) 
    self._performance = False
    self._trash_dir = None
    self.artifacts_dir = None
    self.download_only = False
    self.storage_config = None
    self.ingest_only = False
    self.ingest = False
    self.project_file_variables = key_value_list()
    self.host_project_file_variables = key_value_list()
    self.cli_variables = None
    self.properties_file = None
    self.python_version = self.DEFAULT_PYTHON_VERSION
    
  def builds_dir(self, build_target):
    return path.join(self.build_root, 'builds', build_target.build_path)

  @property
  def build_root(self):
    return self._build_root

  @build_root.setter
  def build_root(self, value):
    self._build_root = value
    self._build_root_changed()
    
  @property
  def performance(self):
    return self._performance

  @property
  def storage_cache_dir(self):
    if not self._build_root:
      raise AttributeError('build_root has not been set yet.')
    return path.join(self._build_root, 'storage')

  @performance.setter
  def performance(self, value):
    if value == self._performance:
      return
    self._performance = value
    if self._performance:
      self.timer = debug_timer('perf', 'info', disabled = False)
      log.configure('perf=info format=brief')
    else:
      self.timer = debug_timer('perf', 'debug', disabled = True) 
  
  def _build_root_changed(self):
    self._trash_dir = path.join(self._build_root, '.trash')

  @property
  def trash_dir(self):
    if not self._trash_dir:
      raise AttributeError('trash_dir has not been set yet.')
    return self._trash_dir

  @trash_dir.setter
  def trash_dir(self, value):
    raise AttributeError('trash_dir is read only.')

  @property
  def is_partial_build(self):
    'Return True if the build is partial - only download or ingest.'
    return self.download_only or self.ingest_only
