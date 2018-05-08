#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

from .value_list_base import value_list_base
from .value_file import value_file

class value_file_list(value_list_base):

  __value_type__ = value_file
  
  def __init__(self, env = None, values = None):
    super(value_file_list, self).__init__(env)

check.register_class(value_file_list, include_seq = False)
