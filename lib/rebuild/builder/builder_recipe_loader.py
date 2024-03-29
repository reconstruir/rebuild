#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.common import check
from bes.fs import file_util

from rebuild.recipe import recipe, recipe_parser

class builder_recipe_loader(object):

  @classmethod
  def load(clazz, env, filename):
    recipes = clazz._load_recipes(env, filename)
    if clazz._recipe_version(filename) == 2:
      return recipes.recipes
    assert False

  _recipes = namedtuple('_recipes', 'filename,recipes')

  @classmethod
  def _load_recipes_v2(clazz, env, filename):
    content = file_util.read(filename, codec = 'utf8')
    parser = recipe_parser(env, filename, content)
    recipes = parser.parse()
    return clazz._recipes(filename, recipes)
  
  @classmethod
  def _load_recipes(clazz, env, filename):
    version =  clazz._recipe_version(filename)
    assert version in [ 2]
    return clazz._load_recipes_v2(env, filename)
  
  @classmethod
  def _recipe_version(clazz, filename):
    with open(filename, 'r') as fin:
      magic = fin.read(len(recipe_parser.MAGIC))
      if magic == recipe_parser.MAGIC:
        return 2
    return 1
