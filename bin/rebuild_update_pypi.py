#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

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

class update_cli(object):
  
  def __init__(self):
    self._parser = argparse.ArgumentParser()
    self._parser.add_argument('recipe_filename', action = 'store', help = 'The recipe to update.')
    self._parser.add_argument('--verbose',
                              '-v',
                              action = 'store_true',
                              default = False,
                              help = 'Verbose debug spew [ False ]')
    self._parser.add_argument('--update',
                              '-u',
                              action = 'store_true',
                              default = False,
                              help = 'Update the recipe version to the latest release [ False ]')
    
  @classmethod
  def run(clazz):
    raise SystemExit(update_cli().main())

  def main(self):
    args = self._parser.parse_args()
    self._process_file(args.recipe_filename, args.update)
    return 0

  def _process_file(self, filename, update):
    if not path.isfile(filename):
      raise IOError('Not a file: %s' % (filename))
    env = testing_recipe_load_env()
    recipes = builder_recipe_loader.load(env, filename)
    for recipe in recipes:
      self._process_recipe(recipe, filename, update)
    return 0

  def _process_recipe(self, recipe, filename, update):
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
        
    file_util.backup(filename)
    new_recipe.save_to_file(filename)
    replacements = {
      'all: ${_url}/${_filename} ingested_filename=${_ingested_filename} checksum=${_checksum}': 'all: ${_url} ingested_filename=${_ingested_filename} checksum=@{DATA:checksum:${_version}}',
    }
    file_replace.replace(filename, replacements, backup = False)
  
  def _make_new_descriptor(clazz, descriptor, new_upstream_version):
    new_version = descriptor.version.clone({ 'upstream_version': new_upstream_version })
    return descriptor.clone({ 'version': new_version })

  def _make_new_data(clazz, data, old_release, new_release):
    dm = recipe_data_manager.from_masked_value_list(data)
    dm.append(recipe_data_entry('all', 'checksum', new_release.version, new_release.checksum))
    dm.append(recipe_data_entry('all', 'path_hash', new_release.version, new_release.path_hash))
    dm.append(recipe_data_entry('all', 'checksum', old_release.version, old_release.checksum))
    dm.append(recipe_data_entry('all', 'path_hash', old_release.version, old_release.path_hash))
    dm.remove_dups()
    dm.sort_by_version()
    return masked_value_list([ recipe_data_manager.parse_entry_text(str(x)) for x in dm ])

  def _make_new_variables(clazz, variables, upstream_name, extension):
    result = masked_value_list()

    texts = [
      '_version=${REBUILD_PACKAGE_UPSTREAM_VERSION}',
      '_upstream_name={}'.format(upstream_name),
      '_filename=${{_upstream_name}}-${{_version}}.{}'.format(extension),
      '_url=https://files.pythonhosted.org/packages/@{DATA:path_hash:${_version}}/${_filename}',
      '_ingested_filename=python/packages/${_filename}',
    ]
    result = masked_value_list()
    for text in texts:
      kvl = key_value_list.parse(text)
      value = value_key_values(origin = None, value = kvl)
      mvl = masked_value('all', value)
      result.append(mvl)
    return result
  
if __name__ == '__main__':
  update_cli.run()
