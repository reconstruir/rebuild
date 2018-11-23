#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check

from .value_file import value_file

class value_dir(value_file):

  def __init__(self, origin = None, filename = '', properties = None):
    'Class to manage a recipe dir.'
    super(value_dir, self).__init__(origin = origin, filename = filename, properties = properties)

check.register_class(value_dir, include_seq = True)
