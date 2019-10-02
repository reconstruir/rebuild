#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path
import pprint


from bes.fs.file_replace import file_replace
from bes.fs.temp_file import temp_file
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
      v = recipe.resolve_variables('linux').to_dict()
      #print(pprint.pformat(v))
      upstream_name = v['_upstream_name']
      data = ingest_pypi.project_info(upstream_name)
      old_version = recipe.descriptor.version.upstream_version
      new_version = data.latest_release.version
      if old_version == new_version:
        print('{}: already at latest version "{}"'.format(new_version))
      else:
        print('         name: {}'.format(recipe.descriptor.name))
        print('upstream_name: {}'.format(upstream_name))
        print('  old_version: {}'.format(old_version))
        print('  new_version: {}'.format(new_version))
        print(' new_checksum: {}'.format(data.latest_release.checksum))

        dm = recipe_data_manager.from_masked_value_list(recipe.data)
        dm.append(recipe_data_entry('all', 'checksum', new_version, data.latest_release.checksum))
        dm.append(recipe_data_entry('all', 'path_hash', new_version, data.latest_release.path_hash))
        dm.sort_by_version()
        recipe.data.assign(masked_value_list([ recipe_data_manager.parse_entry_text(str(x)) for x in dm ]))
        file_util.backup(filename)
        file_util.save(filename, str(recipe))
        
#          print('X: mask={} value={} - {}'.format(x.mask, x.value, type(x.value.value)))
#        for x in recipe.data:
#          print('X: mask={} value={} - {}'.format(x.mask, x.value, type(x.value.value)))
      
#      print(data.latest_release)
      #_upstream_name
#      print(recipe)
#      values = recipe.steps[0].resolve_values({}, env)
#      tarball_address = values.get('tarball_address')
#      if tarball_address:
#        tarball_address_address = tarball_address.address
#        old_revision = tarball_address.revision
#        gr = git_repo(temp_file.make_temp_dir(), address = tarball_address_address)
#        gr.clone()
#        new_revision = gr.last_commit_hash(short_hash = True)
#        if old_revision == new_revision:
#          return 0
#        replacements = { old_revision: new_revision }
#        print('%s: update %s -> %s' % (filename, old_revision, new_revision))
#        file_replace.replace(filename, replacements, backup = False, word_boundary = True)
    return 0
      
if __name__ == '__main__':
  update_cli.run()
