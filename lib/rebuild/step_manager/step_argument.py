#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check_type
import copy

class step_argument(object):

  def __init__(self, script, env, args = {}, last_input = {}):
    if script is None:
      raise RuntimeError('script cannot be None.')
    if env is None:
      raise RuntimeError('env cannot be None.')
    self.script = script
    self.env = env
    check_type.check_dict(args, 'args')
    check_type.check_dict(last_input, 'last_input')
    self.args = copy.deepcopy(args)
    self.last_input = copy.deepcopy(last_input)

  def clone(self):
    return step_argument(self.script, self.env, args = self.args, last_input = self.last_input)

  def update_args(self, args):
    self.args.update(args or {})

  def update_last_input(self, last_input):
    self.last_input.update(last_input or {})
