#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple
from rebuild.base import build_arch, build_level, build_system, build_target
from bes.common import time_util
from bes.debug import debug_timer
from bes.system import log

class builder_config(object):

  DEFAULT_THIRD_PARTY_PREFIX = 'rebbe_'
  
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
    self.skip_tests = False
    self.skip_to_step = None
    self.source_dir = None
    self.source_git = None
    self.source_pcloud = None
    self.third_party_prefix = self.DEFAULT_THIRD_PARTY_PREFIX
    self.timestamp = time_util.timestamp()
    self.tmp_dir = None
    self.tools_only = False
    self.users = False
    self.verbose = False
    self.wipe = False
    self._performance = False
    self.timer = debug_timer('perf', 'debug', disabled = True) 
    self._performance = False
    self._trash_dir = None
    self.artifacts_dir = None
    self.download_only = False
    self.accounts_config = None
    
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
