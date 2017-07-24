#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy

class step_result(object):

  def __init__(self, success, message = None, failed_step = None, output = {}):
    self.success = success
    self.message = message
    self.failed_step = failed_step
    assert isinstance(output, dict)
    self.output = copy.deepcopy(output)

  def __str__(self):
    return '%s:%s:%s:%s' % (self.success, self.message, self.failed_step, self.output)
