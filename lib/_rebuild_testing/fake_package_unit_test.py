#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.fs import temp_file
from bes.common import check

from .fake_package_recipe_parser import fake_package_recipe_parser
from .fake_package_recipe import fake_package_recipe
from rebuild.package import artifact_manager, package

class fake_package_unit_test(object):

  @classmethod
  def create_one_package(clazz, recipe, metadata_mutations = {}, debug = False):
    recipe = clazz._parse_one_recipe(recipe, metadata_mutations)
    tmp_file = temp_file.make_temp_file(delete = not debug)
    if debug:
      print('tmp_file: %s' % (tmp_file))
    return recipe.create_package(tmp_file, debug = debug).filename

  @classmethod
  def create_many_packages(clazz, recipe, metadata_mutations = {}, debug = False):
    recipes = clazz._parse_many_recipes(recipe, metadata_mutations)
    result = []
    for r in recipes:
      tmp_file = temp_file.make_temp_file(delete = not debug)
      if debug:
        print('tmp_file: %s' % (tmp_file))
      result.append(r.create_package(tmp_file, debug = debug).filename)
    return result

  @classmethod
  def _parse_one_recipe(clazz, recipe, metadata_mutations):
    check.check_string(recipe)
    recipes = fake_package_recipe_parser('<unknown>', recipe).parse()
    assert len(recipes) == 1
    return recipes[0]
  
  @classmethod
  def _parse_many_recipes(clazz, recipe, metadata_mutations):
    check.check_string(recipe)
    recipes = fake_package_recipe_parser('<unknown>', recipe).parse()
    result = []
    if metadata_mutations:
      for r in recipes:
        result.append(r.clone_with_mutations(metadata_mutations))
    else:
      result = recipes
    return result

  @classmethod
  def make_artifact_manager(clazz, debug = False, recipes = None, build_target = None, mutations = None):
    root_dir = temp_file.make_temp_dir(delete = not debug)
    if debug:
      print("root_dir:\n%s\n" % (root_dir))
    am = artifact_manager(root_dir)
    if recipes:
      mutations = mutations or {}
      check.check_build_target(build_target)
      tmp_packages = fake_package_unit_test.create_many_packages(recipes, mutations)
      for tmp_package in tmp_packages:
        am.publish(tmp_package, build_target, False)
    return am
