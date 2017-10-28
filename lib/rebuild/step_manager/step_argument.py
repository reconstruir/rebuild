#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

class step_argument(object):

  def __init__(self, script, args = {}, output = {}):
    self.script = script
    assert isinstance(args, dict)
    assert isinstance(output, dict)
    self.args = copy.deepcopy(args)
    self.output = copy.deepcopy(output)

  def clone(self):
    return step_argument(self.script, args = self.args, output = self.output)

  def update_args(self, args):
    self.args.update(args or {})

  def update_output(self, output):
    self.output.update(output or {})
    
