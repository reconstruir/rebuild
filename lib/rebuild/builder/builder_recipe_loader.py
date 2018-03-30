#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.common import check
from bes.fs import file_util

from rebuild.recipe import recipe, recipe_parser

class builder_recipe_loader(object):

  @classmethod
  def load(clazz, filename):
    recipes = clazz._load_recipes(filename)
    if clazz._recipe_version(filename) == 2:
      return recipes.recipes
    assert False

  _recipes = namedtuple('_recipes', 'filename,recipes')

  @classmethod
  def _load_recipes_v2(clazz, filename):
    parser = recipe_parser(file_util.read(filename, codec = 'utf8'), filename)
    recipes = parser.parse()
    return clazz._recipes(filename, recipes)
  
  @classmethod
  def _load_recipes(clazz, filename):
    version =  clazz._recipe_version(filename)
    assert version in [ 2]
    return clazz._load_recipes_v2(filename)
  
  @classmethod
  def _recipe_version(clazz, filename):
    with open(filename, 'r') as fin:
      magic = fin.read(len(recipe_parser.MAGIC))
      if magic == recipe_parser.MAGIC:
        return 2
    return 1
