#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.common import check
from bes.fs import file_util

from rebuild.recipe import recipe, recipe_parser, recipe_parser_error

class builder_recipe_loader(object):

  @classmethod
  def load(clazz, env, filename):
    recipes = clazz._load_recipes(env, filename)
    if clazz._recipe_version(filename) == 2:
      return recipes.recipes
    # This is here in case the recipe version is changed in the future.
    # There was a recipe v1 at some point during development that is retired.
    assert False

  _recipes = namedtuple('_recipes', 'filename,recipes')

  @classmethod
  def _load_recipes_v2(clazz, env, filename):
    content = file_util.read(filename, codec = 'utf8')
    parser = recipe_parser(filename, content)
    recipes = parser.parse()
    return clazz._recipes(filename, recipes)
  
  @classmethod
  def _load_recipes(clazz, env, filename):
    version =  clazz._recipe_version(filename)
    if not version in [ 2 ]:
      raise recipe_parser_error('Invalid recipe magic header', filename, 1)
    return clazz._load_recipes_v2(env, filename)
  
  @classmethod
  def _recipe_version(clazz, filename):
    with open(filename, 'r') as fin:
      magic = fin.read(len(recipe_parser.MAGIC))
      if magic == recipe_parser.MAGIC:
        return 2
    return 1
