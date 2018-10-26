#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.fs import temp_file
from bes.common import check

from .fake_package_recipe_parser import fake_package_recipe_parser
from .fake_package_recipe import fake_package_recipe
from .artifact_manager import artifact_manager
from .package import package

class fake_package_unit_test(object):

  DEBUG = False
  
  @classmethod
  def create_one_package(clazz, recipe, metadata_mutations = {}, debug = False):
    recipe = clazz._parse_one_recipe(recipe, metadata_mutations)
    tmp_file = temp_file.make_temp_file(delete = not debug)
    if debug:
      print('tmp_file: %s' % (tmp_file))
    return recipe.create_package(tmp_file).filename

  @classmethod
  def create_many_packages(clazz, recipe, metadata_mutations = {}, debug = False):
    recipes = clazz._parse_many_recipes(recipe, metadata_mutations)
    result = []
    for r in recipes:
      tmp_file = temp_file.make_temp_file(delete = not debug)
      if debug:
        print('tmp_file: %s' % (tmp_file))
      result.append(r.create_package(tmp_file).filename)
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
  
  WATER_RECIPE = 'fake_package water 1.0.0 0 0 linux release x86_64 ubuntu 18'
  APPLE_RECIPE = '''fake_package apple 1.2.3 1 0 linux release x86_64 ubuntu 18
  requirements
    fruit >= 1.0.0'''
  
  TEST_RECIPES = '''
fake_package water 1.0.0 0 0 linux release x86_64 ubuntu 18

fake_package water 1.0.0 1 0 linux release x86_64 ubuntu 18

fake_package water 1.0.0 2 0 linux release x86_64 ubuntu 18

fake_package fiber 1.0.0 0 0 linux release x86_64 ubuntu 18

fake_package citrus 1.0.0 2 0 linux release x86_64 ubuntu 18

fake_package fructose 3.4.5 6 0 linux release x86_64 ubuntu 18

fake_package mercury 1.2.8 0 0 linux release x86_64 ubuntu 18

fake_package mercury 1.2.8 1 0 linux release x86_64 ubuntu 18

fake_package mercury 1.2.9 0 0 linux release x86_64 ubuntu 18

fake_package arsenic 1.2.9 0 0 linux release x86_64 ubuntu 18

fake_package arsenic 1.2.9 1 0 linux release x86_64 ubuntu 18

fake_package arsenic 1.2.10 0 0 linux release x86_64 ubuntu 18

fake_package apple 1.2.3 1 0 linux release x86_64 ubuntu 18
  requirements
    fruit >= 1.0.0

fake_package fruit  1.0.0 0 0 linux release x86_64 ubuntu 18
  requirements
    fructose >= 3.4.5-6
    fiber >= 1.0.0-0
    water >= 1.0.0-0

fake_package pear 1.2.3 1 0 linux release x86_64 ubuntu 18
  requirements
    fruit >= 1.0.0

fake_package orange 6.5.4 3 0 linux release x86_64 ubuntu 18
  requirements
    fruit >= 1.0.0
    citrus >= 1.0.0

fake_package orange_juice 1.4.5 0 0 linux release x86_64 ubuntu 18
  requirements
    orange >= 6.5.4-3

fake_package pear_juice 6.6.6 0 0 linux release x86_64 ubuntu 18
  requirements
    pear >= 1.2.3-1
    
fake_package smoothie 1.0.0 0 0 linux release x86_64 ubuntu 18
  requirements
    orange >= 6.5.4-3
    pear >= 1.2.3 1-0
    apple >= 1.2.3-1

fake_package knife 1.0.0 0 0 linux release x86_64 ubuntu 18
  files
    bin/cut.sh
      \#!/bin/bash
      echo cut ; exit 0

'''
  