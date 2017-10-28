#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

class step_argument(object):

  def __init__(self, script, args = {}, last_input = {}):
    self.script = script
    assert isinstance(args, dict)
    assert isinstance(last_input, dict)
    self.args = copy.deepcopy(args)
    self.last_input = copy.deepcopy(last_input)

  def clone(self):
    return step_argument(self.script, args = self.args, last_input = self.last_input)

  def update_args(self, args):
    self.args.update(args or {})

  def update_last_input(self, last_input):
    self.last_input.update(last_input or {})
    
