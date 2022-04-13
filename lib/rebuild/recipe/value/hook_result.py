#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from collections import namedtuple

class hook_result(namedtuple('hook_result', 'success, message')):

  DEFAULT = 'default'

  def __new__(clazz, success, message = None):
    check.check_bool(success)
    if message:
      check.check_string(message)
    return clazz.__bases__[0].__new__(clazz, success, message)

  def __str__(self):
    return '%s:%s' % (self.success, self.message)

check.register_class(hook_result, include_seq = False)
