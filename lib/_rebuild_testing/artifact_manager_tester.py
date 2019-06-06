#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.common.check import check
from bes.common.object_util import object_util
from bes.common.string_util import string_util
from bes.fs import temp_file
from bes.text import text_line_parser

from rebuild.package import artifact_manager_local
from rebuild.base import artifact_descriptor

from .fake_package_recipe_parser import fake_package_recipe_parser
from .artifact_manager_helper import artifact_manager_helper

class artifact_manager_tester(object):

  def __init__(self, root_dir = None, debug = False, recipes = None, filename = None):
    root_dir = root_dir or temp_file.make_temp_dir(suffix = '.artifacts', delete = not debug)
    self._debug = debug
    self.am = artifact_manager_helper.make_local_artifact_manager(root_dir)
    self._recipes = {}
    if recipes:
      self.add_recipes(recipes, filename = filename)
      
  def add_recipes(self, recipes, filename = None):
    filename = filename or '<unknown>'
    check.check_string(filename)
    check.check_string(recipes)
    result = {}
    for recipe in fake_package_recipe_parser(filename, recipes).parse():
      key = str(recipe.metadata)
      if key in self._recipes:
        raise RuntimeError('Already in recipes: %s' % (key))
      self._recipes[key] = recipe
      result[key] = recipe
    return result
      
  def clear_recipes(self):
    self._recipes = {}

  def create_package(self, adesc, mutations = {}):
    adesc = self._parse_adesc(adesc)
    key = str(adesc)
    if not key in self._recipes:
      raise KeyError('recipe not found: %s' % (key))
    recipe = self._recipes[key]
    if mutations:
      recipe = recipe.clone(mutations)
    tmp_file = temp_file.make_temp_file()
    return recipe.create_package(tmp_file, debug = self._debug)

  def publish(self, adescs, mutations = {}):
    adescs = self._parse_adesc_list(adescs)
    result = []
    for adesc in adescs:
      result.append(self._publish_one(adesc, mutations))
    return result

  def retire(self, adescs):
    adescs = self._parse_adesc_list(adescs)
    for adesc in adescs:
      self._retire_one(adesc)

  def retire_all(self):
    adescs = self.am.list_all_by_descriptor(None)
    self.retire(adescs)

  def _publish_one(self, adesc, mutations):
    adesc = self._parse_adesc(adesc)
    pkg = self.create_package(adesc, mutations = mutations)
    self.am.publish(pkg.filename, False, pkg.metadata)
    return pkg
  
  def _retire_one(self, adesc):
    adesc = self._parse_adesc(adesc)
    self.am.remove_artifact(adesc)
    
  def dump(self):
    for r in sorted(self._recipes.values()):
      print(r.metadata)

  @classmethod
  def _parse_adesc(clazz, adesc):
    if check.is_string(adesc):
      if adesc.startswith('fake_package'):
        parts = string_util.split_by_white_space(adesc)
        parts = parts[1:]
        adesc = ';'.join(parts)
      adesc = artifact_descriptor.parse(adesc)
    check.check_artifact_descriptor(adesc)
    return adesc

  @classmethod
  def _parse_adesc_list(clazz, adescs):
    if check.is_artifact_descriptor_list(adescs):
      return adescs
    elif check.is_artifact_descriptor(adescs):
      return artifact_descriptor_list([ adescs ])
    elif check.is_string(adescs) and '\n' in adescs:
      adescs = text_line_parser.parse_lines(adescs, strip_text = True, remove_empties = True)
      adescs = [ adesc for adesc in adescs if adesc.startswith('fake_package') ]
    else:
      adescs = object_util.listify(adescs)
    return adescs
