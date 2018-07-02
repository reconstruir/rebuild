#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, type_checked_list
from rebuild.base import package_descriptor_list
from .package import package

class package_list(type_checked_list):

  __value_type__ = package
  
  def __init__(self, values = None):
    super(package_list, self).__init__(values = values)

  def descriptors(self):
    'Return the names for all the descriptors.'
    return package_descriptor_list([ p.descriptor for p in self ])

check.register_class(package_list, include_seq = False)
