#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat import StringIO
from bes.common import check, type_checked_list
from .recipe import recipe
from bes.system.compat import with_metaclass
from bes.common.json_util import serializable_register_meta

class recipe_list(with_metaclass(serializable_register_meta, type_checked_list)):

  __value_type__ = recipe
  
  def __init__(self, values = None):
    super(recipe_list, self).__init__(values = values)

  def to_string(self, delimiter = '\n'):
    buf = StringIO()
    first = True
    for recipe in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(recipe))
    return buf.getvalue()

  def __hash__(self):
    return hash(str(self))
  
  def __str__(self):
    return self.to_string()

check.register_class(recipe_list, include_seq = False)
