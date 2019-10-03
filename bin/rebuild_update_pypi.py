#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path
import pprint

from bes.fs.file_replace import file_replace
from bes.fs.temp_file import temp_file
from bes.fs.file_util import file_util
from bes.git.git_repo import git_repo

from rebuild.builder.builder_recipe_loader import builder_recipe_loader
from rebuild.ingest.ingest_pypi import ingest_pypi
from rebuild.recipe.recipe_load_env import testing_recipe_load_env
from rebuild.recipe.recipe_data_manager import recipe_data_manager
from rebuild.recipe.recipe_data_entry import recipe_data_entry
from rebuild.recipe.recipe_data_entry import recipe_data_entry_list
from rebuild.recipe.value.masked_value_list import masked_value_list

class update_cli(object):
  
  def __init__(self):
    self._parser = argparse.ArgumentParser()
    self._parser.add_argument('recipe_filename', action = 'store', help = 'The recipe to update.')
    self._parser.add_argument('--verbose',
                              '-v',
                              action = 'store_true',
                              default = False,
                              help = 'Verbose debug spew [ False ]')
    
  @classmethod
  def run(clazz):
    raise SystemExit(update_cli().main())

  def main(self):
    args = self._parser.parse_args()
    self._process_file(args.recipe_filename)
    return 0

  def _process_file(self, filename):
    if not path.isfile(filename):
      raise IOError('Not a file: %s' % (filename))
    env = testing_recipe_load_env()
    recipes = builder_recipe_loader.load(env, filename)
    for recipe in recipes:
      system = 'linux' # doesnt matter just needs to be a valid system
      vars_kvl = recipe.resolve_variables('linux')
      vars_dict = vars_kvl.to_dict()
      #print(vars_kvl.to_string(value_delimiter = '\n'))
      upstream_name = vars_dict['_upstream_name']
      pypi_data = ingest_pypi.project_info(upstream_name)
      old_version = recipe.descriptor.version.upstream_version
      new_version = pypi_data.latest_release.version
      
      if old_version == new_version:
        print('{}: already at latest version "{}"'.format(new_version))
      else:
        print('         name: {}'.format(recipe.descriptor.name))
        print('upstream_name: {}'.format(upstream_name))
        print('  old_version: {}'.format(old_version))
        print('  new_version: {}'.format(new_version))

        old_release = pypi_data.find_by_version(old_version)
        new_release = pypi_data.latest_release
        
        dm = recipe_data_manager.from_masked_value_list(recipe.data)
        dm.append(recipe_data_entry('all', 'checksum', new_version, new_release.checksum))
        dm.append(recipe_data_entry('all', 'path_hash', new_version, new_release.path_hash))
        dm.append(recipe_data_entry('all', 'checksum', old_version, old_release.checksum))
        dm.append(recipe_data_entry('all', 'path_hash', old_version, old_release.path_hash))
        dm.remove_dups()
        dm.sort_by_version()
        recipe.data.assign(masked_value_list([ recipe_data_manager.parse_entry_text(str(x)) for x in dm ]))
        
        file_util.backup(filename)
        recipe.save_to_file(filename)
        
    return 0
      
if __name__ == '__main__':
  update_cli.run()
