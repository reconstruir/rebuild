#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check, type_checked_list
from bes.dependency import dependency_provider

class recipe_file(dependency_provider):

  def __init__(self, filename):
    'Create a new hook.'
    self.filename = filename

  def value_to_string(self):
    return path.basename(self.filename)
    
  def provided(self):
    'Return a list of dependencies provided by this provider.'
    return [ self.filename ]

class recipe_file_list(type_checked_list):

  def __init__(self, values = None):
    super(recipe_file_list, self).__init__(recipe_file, values = values)

  def __str__(self):
    return self.to_string()

check.register_class(recipe_file, include_seq = False)
check.register_class(recipe_file_list, include_seq = False)
