#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from bes.system.check import check

from collections import namedtuple

class step_result(namedtuple('step_result', 'success, message, failed_step, outputs, stdout')):

  def __new__(clazz, success, message = None, failed_step = None, outputs = None, stdout = None):
    check.check_bool(success)
    if message:
      check.check_string(message)
    if outputs:
      outputs = copy.copy(outputs)
    else:
      outputs = {}
    check.check_dict(outputs)
    return clazz.__bases__[0].__new__(clazz, success, message, failed_step, outputs, stdout)

  def __str__(self):
    return '%s:%s:%s:%s' % (self.success, self.message, self.failed_step, self.outputs)
