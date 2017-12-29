#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.common import check
from rebuild.dependency import dependency_provider

class recipe_file(dependency_provider):

  def __init__(self, filename):
    'Create a new hook.'
    self.filename = filename

  @property
  def name(self):
    return path.basename(self.filename)
    
  def provided(self):
    'Return a list of dependencies provided by this provider.'
    return [ self.filename ]
    
check.register_class(recipe_file)
