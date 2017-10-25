#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from rebuild import build_target

class rebuild_config(object):

  DEFAULT_THIRD_PARTY_ADDRESS = 'git@git:third_party_sources.git'
  DEFAULT_THIRD_PARTY_PREFIX = 'rebbe_'
  
  def __init__(self):
    self.build_target = build_target()
    self.deps_only = False
    self.disabled = False
    self.keep_going = False
    self.no_checksums = False
    self.no_network = False
    self.skip_tests = False
    self.skip_to_step = None
    self.source_dir = None
    self.tools_only = False
    self.third_party_address = self.DEFAULT_THIRD_PARTY_ADDRESS
    self.users = False
    self.verbose = False
    self.wipe = False
    self.third_party_prefix = self.DEFAULT_THIRD_PARTY_PREFIX
