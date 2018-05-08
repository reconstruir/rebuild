#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat import StringIO
from bes.common import check, type_checked_list
from .artifact_descriptor import artifact_descriptor

class artifact_descriptor_list(type_checked_list):

  __value_type__ = artifact_descriptor
  
  def __init__(self, values = None):
    super(artifact_descriptor_list, self).__init__(values = values)

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

check.register_class(artifact_descriptor_list, include_seq = False)