#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.fs import temp_file

from .fake_package_recipe_parser import fake_package_recipe_parser
from .fake_package_recipe import fake_package_recipe

class fake_package_unit_test(object):

  @classmethod
  def create_one_package(clazz, recipe):
    recipe = clazz._parse_one_recipe(recipe)
    return recipe.create_package(temp_file.make_temp_file()).filename

  @classmethod
  def _parse_one_recipe(clazz, recipe):
    if isinstance(recipe, fake_package_recipe):
      return recipe
    recipes = fake_package_recipe_parser('<unknown>', recipe).parse()
    assert len(recipes) == 1
    return recipes[0]
  
