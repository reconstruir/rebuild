#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple
from rebuild.base import build_arch, build_level, build_system, build_target
from bes.common import time_util
from bes.debug import debug_timer, noop_debug_timer
from bes.system import log

class builder_config(object):

  DEFAULT_THIRD_PARTY_ADDRESS = 'git@git:third_party_tarballs.git'
  DEFAULT_THIRD_PARTY_PREFIX = 'rebbe_'
  
  def __init__(self):
    self.build_root = None
    self.build_target = build_target()
    self.host_build_target = build_target(system = build_system.HOST,
                                          level = build_level.RELEASE,
                                          archs = build_arch.DEFAULT_HOST_ARCHS)
    self.root_dir = None
    self.deps_only = False
    self.recipes_only = False
    self.disabled = False
    self.keep_going = False
    self.no_checksums = False
    self.no_network = False
    self.skip_tests = False
    self.skip_to_step = None
    self.source_dir = None
    self.tools_only = False
    self.third_party_address = self.DEFAULT_THIRD_PARTY_ADDRESS
    self.tmp_dir = None
    self.users = False
    self.verbose = False
    self.wipe = False
    self.scratch = False
    self.third_party_prefix = self.DEFAULT_THIRD_PARTY_PREFIX
    self.timestamp = time_util.timestamp()
    self._performance = False
    self.timer = noop_debug_timer('perf', 'debug') 
    
  def builds_dir(self, build_target):
    return path.join(self.build_root, 'builds', build_target.build_path)

  @property
  def performance(self):
    return self._performance

  @performance.setter
  def performance(self, value):
    if value == self._performance:
      return
    self._performance = value
    if self._performance:
      self.timer = debug_timer('perf', 'info')
      log.configure('perf=info format=brief')
    else:
      self.timer = noop_debug_timer('perf', 'debug') 
  
