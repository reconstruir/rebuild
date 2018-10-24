#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.fs import temp_file
from bes.common import check

from .fake_package_recipe_parser import fake_package_recipe_parser
from .fake_package_recipe import fake_package_recipe

class fake_package_unit_test(object):

  @classmethod
  def create_one_package(clazz, recipe, metadata_mutations = {}):
    recipe = clazz._parse_one_recipe(recipe, metadata_mutations)
    return recipe.create_package(temp_file.make_temp_file()).filename

  @classmethod
  def create_many_packages(clazz, recipe, metadata_mutations = {}):
    recipes = clazz._parse_many_recipes(recipe, metadata_mutations)
    result = []
    for r in recipes:
      result.append(r.create_package(temp_file.make_temp_file()).filename)
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
