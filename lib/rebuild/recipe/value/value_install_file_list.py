#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, type_checked_list

from .value_base import value_base
from .value_install_file import value_install_file

class value_install_file_list(type_checked_list):

  __value_type__ = value_install_file
  
  def __init__(self, values = None):
    super(value_install_file_list, self).__init__(values = values)

  def __str__(self):
    return self.to_string()
  
check.register_class(value_install_file_list, include_seq = False)
