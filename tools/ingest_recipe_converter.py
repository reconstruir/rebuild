#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path
from collections import namedtuple

from bes.fs.file_resolve import file_resolve


import argparse, os.path as path
import pprint

from bes.archive.archive_extension import archive_extension
from bes.fs.file_util import file_util
from bes.fs.file_replace import file_replace
from bes.key_value.key_value_list import key_value_list

from rebuild.builder.builder_recipe_loader import builder_recipe_loader

from rebuild.ingest.ingest_pypi import ingest_pypi

from rebuild.recipe.recipe_data_entry import recipe_data_entry
from rebuild.recipe.recipe_data_entry import recipe_data_entry_list
from rebuild.recipe.recipe_data_manager import recipe_data_manager
from rebuild.recipe.recipe_load_env import testing_recipe_load_env
from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.value.value_key_values import value_key_values

from rebuild.recipe.value.value_source_tarball import value_source_tarball
from rebuild.recipe.value.value_git_address import value_git_address

class ingest_recipe_converter(object):

  def __init__(self):
    self.parser = argparse.ArgumentParser()
    self.parser.add_argument('where', action = 'store', help = 'The dir to find recipes in')

  def main(self):
    args = self.parser.parse_args()

    files = file_resolve.resolve_dir(args.where, patterns = [ '*.recipe' ])
    for rf in files:
      self._process_file(rf.filename_abs)
    
    return 0

  def _process_file(self, filename):
    if not path.isfile(filename):
      raise IOError('Not a file: %s' % (filename))
    env = testing_recipe_load_env()
    env.variable_manager.add_variable('REBUILD_PYTHON_VERSION', '2.7')
    recipes = builder_recipe_loader.load(env, filename)
    for recipe in recipes:
      self._process_recipe(recipe, filename)
    return 0

  def _process_recipe(self, recipe, filename):
    ingest_info = self._find_recipe_ingest_info(recipe)
    if ingest_info:
      print('{}: method={} values={}'.format(filename, ingest_info.method, ingest_info.values))
    else:
      print('{}: NOT'.format(filename))

  @classmethod
  def _find_recipe_upstream_source(clazz, recipe):
    values = recipe.find_step_values('*', 'upstream_source')
    if not values:
      return None
    for v in values:
      if isinstance(v.value, value_source_tarball):
        result = { 'url': v.value.value }
        result.update(v.value.properties.to_dict())
        return result
    return None

  @classmethod
  def _find_recipe_tarball_address(clazz, recipe):
    values = recipe.find_step_values('*', 'tarball_address')
    if not values:
      return None
    for v in values:
      if isinstance(v.value, value_git_address):
        result = {
          'address': v.value.value.address,
          'revision': v.value.value.revision,
        }
        result.update(v.value.properties.to_dict())
        return result
    return None

  _found_ingest_info = namedtuple('_found_ingest_info', 'method, data, variables, values')

  @classmethod
  def _find_recipe_ingest_info(clazz, recipe):
    upstream_source = clazz._find_recipe_upstream_source(recipe)
    if upstream_source:
      return clazz._found_ingest_info('http', recipe.data, recipe.variables, upstream_source)
    tarball_address = clazz._find_recipe_tarball_address(recipe)
    if tarball_address:
      return clazz._found_ingest_info('git', recipe.data, recipe.variables, tarball_address)
    return None
  
  @classmethod
  def run(clazz):
    raise SystemExit(ingest_recipe_converter().main())
  
if __name__ == '__main__':
  ingest_recipe_converter.run()
  
