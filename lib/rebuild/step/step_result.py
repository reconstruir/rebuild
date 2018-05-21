#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from bes.common import check

from collections import namedtuple

class step_result(namedtuple('step_result', 'success, message, failed_step, outputs')):

  def __new__(clazz, success, message = None, failed_step = None, outputs = None):
    check.check_bool(success)
    if message:
      check.check_string(message)
    if outputs:
      check.check_dict(outputs)
      outputs = copy.deepcopy(outputs)
    else:
      outputs = {}
    return clazz.__bases__[0].__new__(clazz, success, message, failed_step, outputs)

  def __str__(self):
    return '%s:%s:%s:%s' % (self.success, self.message, self.failed_step, self.outputs)
