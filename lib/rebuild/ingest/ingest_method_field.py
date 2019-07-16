#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check

from collections import namedtuple

class ingest_method_field(namedtuple('ingest_method_field', 'key, optional')):
  def __new__(clazz, key, optional = False):
    check.check_string(key)
    check.check_bool(optional)
    return clazz.__bases__[0].__new__(clazz, key, optional)
