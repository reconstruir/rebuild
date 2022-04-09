#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path
from collections import namedtuple

from bes.fs.file_resolver import file_resolver
from bes.fs.file_resolver_options import file_resolver_options
from bes.fs.file_util import file_util
from bes.fs.file_replace import file_replace
from bes.key_value.key_value_list import key_value_list

from rebuild.builder.builder_recipe_loader import builder_recipe_loader

from rebuild.ingest.ingest_method_descriptor_git import ingest_method_descriptor_git
from rebuild.ingest.ingest_method_descriptor_http import ingest_method_descriptor_http
from rebuild.ingest.ingest_entry import ingest_entry
from rebuild.ingest.ingest_entry_list import ingest_entry_list
from rebuild.ingest.ingest_method import ingest_method
from rebuild.ingest.ingest_file import ingest_file

from rebuild.recipe.recipe_load_env import testing_recipe_load_env
from rebuild.recipe.value.value_git_address import value_git_address
from rebuild.recipe.value.value_source_tarball import value_source_tarball
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.value_key_values import value_key_values

class ingest_recipe_converter(object):

  def __init__(self):
    self.parser = argparse.ArgumentParser()
    self.parser.add_argument('source', action = 'store',
                             help = 'The source dir to scan for rebuild recipes.')
    self.parser.add_argument('destination', action = 'store',
                             help = 'The destination dir where to write ingest recipes.')

  def main(self):
    args = self.parser.parse_args()

    self.replacements = {
      'REBUILD_PACKAGE_UPSTREAM_VERSION': 'VERSION',
    }

    options = file_resolver_options(recursive = True,
                                    match_patterns = [ '*.recipe' ],
                                    match_basename = True)
    files = file_resolver.resolve_files([ args.source ] + args, options = options)
    for rf in files:
      self._process_file(rf.filename_abs,
                         args.source,
                         args.destination)
    
    return 0

  def _process_file(self, filename, source, destination):
    if not path.isfile(filename):
      raise IOError('Not a file: %s' % (filename))
    env = testing_recipe_load_env()
    env.variable_manager.add_variable('REBUILD_PYTHON_VERSION', '2.7')
    env.variable_manager.add_variable('BES_VERSION', '0.0.0')
    env.variable_manager.add_variable('REBUILD_VERSION', '0.0.0')
    env.variable_manager.add_variable('REBUILD_PACKAGE_UPSTREAM_VERSION', '${VERSION}')
    recipes = builder_recipe_loader.load(env, filename)
    entries = ingest_entry_list()
    for recipe in recipes:
      entry = self._rebuild_recipe_to_ingest_recipe(recipe, filename)
      if not entry:
        print('FAILED: {}'.format(filename))
        return 0
      entries.append(entry)
    assert entries
    basename = '{}.reingest'.format(entries[0].name)
    dirname = path.dirname(file_util.remove_head(filename, source))
    dest_filename = path.join(destination, dirname, basename)
    dest_ingest_file = ingest_file(ingest_file.FORMAT_VERSION,
                                   dest_filename,
                                   None,
                                   None,
                                   entries)
    file_util.save(dest_filename, content = str(dest_ingest_file)) 
    print(' DONE: {}'.format(dest_filename))
    file_replace.replace(dest_filename,
                         self.replacements,
                         backup = False,
                         word_boundary = False)
    return 0

  def _rebuild_recipe_to_ingest_recipe(self, recipe, filename):
    ingest_info = self._find_recipe_ingest_info(recipe)
    if not ingest_info:
      return None
    if False:
      print('{}: name={} version={} method={} values={}'.format(filename,
                                                                recipe.name,
                                                                recipe.upstream_version,
                                                                ingest_info.method_descriptor.method,
                                                                ingest_info.values))
    name = recipe.name
    version = recipe.upstream_version
    description = None
    data = ingest_info.data
    variables = ingest_info.variables
    method = self._make_ingest_method(ingest_info)
    return ingest_entry(name, version, description, data, variables, method)

  @classmethod
  def _make_ingest_method(clazz, ingest_info):
    values = masked_value_list()
    if ingest_info.method_descriptor.method() == 'http':
      url = ingest_info.values['url']
      url_kv = key_value_list.parse('url={}'.format(url))
      checksum = ingest_info.values['checksum']
      checksum_kv = key_value_list.parse('checksum={}'.format(checksum))
      ingested_filename = ingest_info.values['ingested_filename']
      ingested_filename_kv = key_value_list.parse('ingested_filename={}'.format(ingested_filename))
      values.append(masked_value('all',
                                 value_key_values(origin = None, value = url_kv), origin = None))
      values.append(masked_value('all',
                                 value_key_values(origin = None, value = checksum_kv), origin = None))
      values.append(masked_value('all',
                                 value_key_values(origin = None, value = ingested_filename_kv), origin = None))
      
    elif ingest_info.method_descriptor.method() == 'git':
      address = ingest_info.values['address']
      address_kv = key_value_list.parse('address={}'.format(address))
      revision = ingest_info.values['revision']
      revision_kv = key_value_list.parse('revision={}'.format(revision))
      ingested_filename = 'fixme/${NAME}-${VERSION}.tar.gz'
      ingested_filename_kv = key_value_list.parse('ingested_filename={}'.format(ingested_filename))
      values.append(masked_value('all',
                                 value_key_values(origin = None, value = address_kv), origin = None))
      values.append(masked_value('all',
                                 value_key_values(origin = None, value = revision_kv), origin = None))
      values.append(masked_value('all',
                                 value_key_values(origin = None, value = ingested_filename_kv), origin = None))
    
    return ingest_method(ingest_info.method_descriptor, values)
    
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

  @classmethod
  def _find_recipe_ingest_info(clazz, recipe):
    upstream_source = clazz._find_recipe_upstream_source(recipe)
    if upstream_source:
      return found_ingest_info(ingest_method_descriptor_http(),
                               recipe.data,
                               recipe.variables,
                               upstream_source)
    tarball_address = clazz._find_recipe_tarball_address(recipe)
    if tarball_address:
      return found_ingest_info(ingest_method_descriptor_git(),
                               recipe.data,
                               recipe.variables,
                               tarball_address)
    return None

  @classmethod
  def run(clazz):
    raise SystemExit(ingest_recipe_converter().main())

class found_ingest_info(namedtuple('found_ingest_info', 'method_descriptor, data, variables, values')):

  def __new__(clazz, method_descriptor, data, variables, values):
    return clazz.__bases__[0].__new__(clazz, method_descriptor, data, variables, values)
  
if __name__ == '__main__':
  ingest_recipe_converter.run()
  
