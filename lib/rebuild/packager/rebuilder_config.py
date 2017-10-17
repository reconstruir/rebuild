#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

class rebuilder_config(object):

  DEFAULT_TPS_ADDRESS = 'git@git:third_party_sources.git'
  
  def __init__(self):
    self.keep_going = False
    self.disabled = False
    self.users = False
    self.deps_only = False
    self.skip_to_step = None
    self.tools_only = False
    self.no_network = False
    self.skip_tests = False
    self.tps_address = self.DEFAULT_TPS_ADDRESS
