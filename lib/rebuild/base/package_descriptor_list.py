#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat import StringIO
from bes.common import check, type_checked_list
from .package_descriptor import package_descriptor

class package_descriptor_list(type_checked_list):

  def __init__(self, values = None):
    super(package_descriptor_list, self).__init__(package_descriptor, values = values)

  def to_string(self, delimiter = '\n'):
    buf = StringIO()
    first = True
    for pd in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(pd))
    return buf.getvalue()

  def __str__(self):
    return self.to_string()

  def names(self):
    'Return the names for all the descriptors.'
    return [ pd.name for pd in self ]

check.register_class(package_descriptor_list, include_seq = False)
