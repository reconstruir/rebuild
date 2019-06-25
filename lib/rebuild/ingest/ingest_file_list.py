#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat.StringIO import StringIO
from bes.common.check import check
from bes.common.type_checked_list import type_checked_list

from .ingest_file import ingest_file

class ingest_file_list(type_checked_list):

  __value_type__ = ingest_file
  
  def __init__(self, values = None):
    super(ingest_file_list, self).__init__(values = values)

  def to_string(self, delimiter = '\n'):
    buf = StringIO()
    first = True
    for ingest_file in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(ingest_file))
    return buf.getvalue()

  def __hash__(self):
    return hash(str(self))
  
  def __str__(self):
    return self.to_string()

check.register_class(ingest_file_list, include_seq = False)
