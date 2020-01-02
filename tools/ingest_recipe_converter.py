#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path
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

class ingest_recipe_converter(object):

  def __init__(self):
    self.parser = argparse.ArgumentParser()
    self.parser.add_argument('where', action = 'store', help = 'The dir to find recipes in')

  def main(self):
    args = self.parser.parse_args()
    print('where: {}'.format(args.where))

    files = file_resolve.resolve_dir(args.where, patterns = [ '*.recipe' ])
    for rf in files:
      self._process_file(rf.filename_abs, True, True)
    
    return 0

  def _process_file(self, filename, update, backup):
    if not path.isfile(filename):
      raise IOError('Not a file: %s' % (filename))
    env = testing_recipe_load_env()
    env.variable_manager.add_variable('REBUILD_PYTHON_VERSION', '2.7')
    print('loading {}'.format(filename))
    recipes = builder_recipe_loader.load(env, filename)
#    for recipe in recipes:
#      self._process_recipe(recipe, filename, update, backup)
    return 0

  def _process_recipe(self, recipe, filename, update, backup):
    print(recipe)
    return
    system = 'linux' # doesnt matter just needs to be a valid system
    vars_kvl = recipe.resolve_variables('linux')
    vars_dict = vars_kvl.to_dict()
    #print(vars_kvl.to_string(value_delimiter = '\n'))
    upstream_name = vars_dict['_upstream_name']
    pypi_data = ingest_pypi.project_info(upstream_name)
    old_version = recipe.descriptor.version.upstream_version
    new_version = pypi_data.latest_release.version
      
    old_release = pypi_data.find_by_version(old_version)
    new_release = pypi_data.latest_release

    if update:
      extension = archive_extension.extension_for_filename(path.basename(new_release.url))
    else:
      extension = archive_extension.extension_for_filename(path.basename(old_release.url))
      
    print('         name: {}'.format(recipe.descriptor.name))
    print('upstream_name: {}'.format(upstream_name))
    print('  old_version: {}'.format(old_version))
    print('  new_version: {}'.format(new_version))
    print('    extension: {}'.format(extension))
    
    mutations = {
      'data': self._make_new_data(recipe.data, old_release, new_release),
      'variables': self._make_new_variables(recipe.variables, upstream_name, extension),
    }
    if update:
      mutations['descriptor'] = self._make_new_descriptor(recipe.descriptor, new_version)
          
    new_recipe = recipe.clone(mutations = mutations)

    if backup:
      file_util.backup(filename)
    new_recipe.save_to_file(filename)
    replacements = {
      'all: ${_url}/${_filename} ingested_filename=${_ingested_filename} checksum=${_checksum}': 'all: ${_url} ingested_filename=${_ingested_filename} checksum=@{DATA:checksum:${_version}}',
    }
    file_replace.replace(filename, replacements, backup = False)
  
  @classmethod
  def run(clazz):
    raise SystemExit(ingest_recipe_converter().main())
  
if __name__ == '__main__':
  ingest_recipe_converter.run()
  
