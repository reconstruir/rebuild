#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step, step_aborted

class step_abort(step):
  'step_abort'

  def __init__(self):
    super(step_abort, self).__init__()

  def execute(self, script, env, args):
    raise step_aborted()
