#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check_type
import copy

class step_argument(object):

  def __init__(self, script, env, args = {}):
    if script is None:
      raise RuntimeError('script cannot be None.')
    if env is None:
      raise RuntimeError('env cannot be None.')
    self.script = script
    self.env = env
    check_type.check_dict(args, 'args')
    self.args = copy.deepcopy(args)

  def clone(self):
    return step_argument(self.script, self.env, args = self.args)

  def update_args(self, args):
    self.args.update(args or {})
