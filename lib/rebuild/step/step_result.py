#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from bes.common import check

class step_result(object):

  def __init__(self, success, message = None, failed_step = None, outputs = {}):
    check.check_bool(success)
    self.success = success
    if message:
      check.check_string(message)
    self.message = message
    self.failed_step = failed_step
    check.check_dict(outputs)
    self.outputs = copy.deepcopy(outputs)

  def __str__(self):
    return '%s:%s:%s:%s' % (self.success, self.message, self.failed_step, self.outputs)
