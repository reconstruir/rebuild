#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import Step, step_aborted

class step_abort(Step):
  'step_abort'

  def __init__(self):
    super(step_abort, self).__init__()

  def execute(self, argument):
    raise step_aborted()
