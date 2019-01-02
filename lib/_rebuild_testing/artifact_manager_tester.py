#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common import check, object_util
from bes.fs import temp_file

from rebuild.package import artifact_manager_local
from rebuild.base import artifact_descriptor

from .fake_package_recipe_parser import fake_package_recipe_parser
from .artifact_manager_helper import artifact_manager_helper

class artifact_manager_tester(object):

  def __init__(self, root_dir = None, debug = False, recipes = None, filename = None):
    root_dir = root_dir or temp_file.make_temp_dir(suffix = '.artifacts')
    self._debug = debug
    self.am = artifact_manager_helper.make_local_artifact_manager(root_dir)
    self._recipes = {}
    if recipes:
      self.add_recipes(recipes, filename = filename)
      
  def add_recipes(self, recipes, filename = None):
    filename = filename or '<unknown>'
    check.check_string(filename)
    check.check_string(recipes)
    for recipe in fake_package_recipe_parser(filename, recipes).parse():
      key = str(recipe.metadata)
      if key in self._recipes:
        raise RuntimeError('Already in recipes: %s' % (key))
      self._recipes[key] = recipe

  def clear_recipes(self):
    self._recipes = {}

  def create_package(self, adesc, mutations = {}):
    if check.is_string(adesc):
      adesc = artifact_descriptor.parse(adesc)
    check.check_artifact_descriptor(adesc)
    key = str(adesc)
    if not key in self._recipes:
      raise KeyError('recipe not found: %s' % (key))
    recipe = self._recipes[key]
    if mutations:
      recipe = recipe.clone(mutations)
    tmp_file = temp_file.make_temp_file()
    return recipe.create_package(tmp_file, debug = self._debug)

  def publish(self, adescs, mutations = {}):
    adescs = object_util.listify(adescs)
    for adesc in adescs:
      self._publish_one(adesc, mutations)

  def retire(self, adescs):
    adescs = object_util.listify(adescs)
    for adesc in adescs:
      self._retire_one(adesc)

  def retire_all(self):
    adescs = self.am.list_all_by_descriptor(None)
    self.retire(adescs)

  def _publish_one(self, adesc, mutations):
    if check.is_string(adesc):
      adesc = artifact_descriptor.parse(adesc)
    check.check_artifact_descriptor(adesc)
    pkg = self.create_package(adesc, mutations = mutations)
    self.am.publish(pkg.filename, False, pkg.metadata)

  def _retire_one(self, adesc):
    if check.is_string(adesc):
      adesc = artifact_descriptor.parse(adesc)
    check.check_artifact_descriptor(adesc)
    self.am.remove_artifact(adesc)
    
  def dump(self):
    for r in sorted(self._recipes.values()):
      print(r.metadata)
