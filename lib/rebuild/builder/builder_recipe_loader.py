#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.system.check import check
from bes.fs.file_util import file_util

from rebuild.recipe.recipe import recipe
from rebuild.recipe.recipe_error import recipe_error
from rebuild.recipe.recipe_parser import recipe_parser

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
  def _test_pickle(clazz, filename, recipe):
    check.check_recipe(recipe)
    import pickle
    try:
      picked_recipe = pickle.dumps(recipe)
    except Exception as ex:
      print('BAD: failed to pickle %s %s: %s' % (filename, recipe.descriptor.name, str(ex)))
      return
    try:
      unpicked_recipe = pickle.loads(picked_recipe)
    except Exception as ex:
      print('BAD: failed to unpickle %s %s: %s' % (filename, recipe.descriptor.name, str(ex)))
      return

    try:
      assert recipe == unpicked_recipe
    except Exception as ex:
      print('BAD: failed to assert unpickled same as original %s %s: %s' % (filename, recipe.descriptor.name, str(ex)))

  
  @classmethod
  def _load_recipes_v2(clazz, env, filename):
    check.check_recipe_load_env(env)
    check.check_variable_manager(env.variable_manager)
    check.check_string(filename)
    content = file_util.read(filename, codec = 'utf8')
    parser = recipe_parser(filename, content)
    recipes = parser.parse(env.variable_manager)

    if False:
#    if True:
      for r in recipes:
        clazz._test_pickle(filename, r)
        
    return clazz._recipes(filename, recipes)
  
  @classmethod
  def _load_recipes(clazz, env, filename):
    version =  clazz._recipe_version(filename)
    if not version in [ 2 ]:
      raise recipe_error('Invalid recipe magic header', filename, 1)
    return clazz._load_recipes_v2(env, filename)
  
  @classmethod
  def _recipe_version(clazz, filename):
    with open(filename, 'r') as fin:
      magic = fin.read(len(recipe.MAGIC))
      if magic == recipe.MAGIC:
        return 2
    return 1
