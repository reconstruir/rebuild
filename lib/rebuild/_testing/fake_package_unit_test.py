#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.system.log import log
from bes.fs.temp_file import temp_file
from bes.system.check import check

from .fake_package_recipe_parser import fake_package_recipe_parser
from .fake_package_recipe import fake_package_recipe
from rebuild.package.package import package

from .artifact_manager_helper import artifact_manager_helper

class fake_package_unit_test(object):

  @classmethod
  def create_one_package(clazz, recipe, metadata_mutations = {}, debug = False):
    recipe = clazz._parse_one_recipe(recipe, metadata_mutations)
    tmp_file = temp_file.make_temp_file(delete = not debug)
    if debug:
      print('tmp_file: %s' % (tmp_file))
    return recipe.create_package(tmp_file, debug = debug)

  @classmethod
  def create_many_packages(clazz, recipe, metadata_mutations = {}, debug = False):
    recipes = clazz._parse_many_recipes(recipe, metadata_mutations)
    result = []
    for r in recipes:
      tmp_file = temp_file.make_temp_file(delete = not debug)
      if debug:
        print('tmp_file: %s' % (tmp_file))
      result.append(r.create_package(tmp_file, debug = debug))
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
        result.append(r.clone(metadata_mutations))
    else:
      result = recipes
    return result

  @classmethod
  def make_artifact_manager(clazz, debug = False, recipes = None, mutations = None):
    root_dir = temp_file.make_temp_dir(delete = not debug)
    if debug:
      print("root_dir:\n%s\n" % (root_dir))
    am = artifact_manager_helper.make_local_artifact_manager(root_dir)
    if recipes:
      clazz.artifact_manager_publish(am, recipes, mutations = mutations)
    return am

  @classmethod
  def artifact_manager_publish(clazz, artifact_manager, recipes, mutations = None):
    mutations = mutations or {}
    tmp_packages = fake_package_unit_test.create_many_packages(recipes, mutations)
    for tmp_package in tmp_packages:
      clazz.log_d('CACA: artifact_manager_publish: id=%s; tmp_package: %s' % (id(artifact_manager), tmp_package.metadata.artifact_descriptor))
      artifact_manager.publish(tmp_package.filename, False, tmp_package.metadata)
  
  @classmethod
  def artifact_manager_clear(clazz, artifact_manager):
    adescs = artifact_manager.list_all_by_descriptor(None)
    for adesc in adescs:
      artifact_manager.remove_artifact(adesc)
      
log.add_logging(fake_package_unit_test)
