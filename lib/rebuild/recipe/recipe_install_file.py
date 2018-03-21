#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from bes.dependency import dependency_provider

class recipe_install_file(dependency_provider):

  def __init__(self, filename, target_filename):
    'Create a new hook.'
    self.filename = filename
    self.target_filename = target_filename

  def value_to_string(self):
    return '%s %s' % (path.basename(self.filename), self.target_filename)
    
  def provided(self):
    'Return a list of dependencies provided by this provider.'
    return [ self.filename ]
    
check.register_class(recipe_install_file)
