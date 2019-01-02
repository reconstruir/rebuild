#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat import StringIO
from bes.common import check, type_checked_list

from .venv_project_config import venv_project_config

class venv_project_config_list(type_checked_list):

  __value_type__ = venv_project_config
  
  def __init__(self, values = None):
    super(venv_project_config_list, self).__init__(values = values)

  def to_string(self, delimiter = '\n'):
    buf = StringIO()
    first = True
    for vc in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(vc))
    return buf.getvalue()

  def __hash__(self):
    return hash(str(self))
  
  def __str__(self):
    return self.to_string()

check.register_class(venv_project_config_list, include_seq = False)
