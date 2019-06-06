#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import argparse, os.path as path
from rebuild.builder.builder_recipe_loader import builder_recipe_loader
from bes.git import repo
from bes.fs.file_replace import file_replace
from bes.fs.temp_file import temp_file
from rebuild.recipe import testing_recipe_load_env

class update_cli(object):
  
  def __init__(self):
    self._parser = argparse.ArgumentParser()
    self._parser.add_argument('files', nargs = '+', action = 'store', help = 'Files or directories to find')
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
    for f in args.files:
      self._process_file(f)
    return 0

  def _process_file(self, filename):
    if not path.isfile(filename):
      raise IOError('Not a file: %s' % (filename))
    env = testing_recipe_load_env()
    recipes = builder_recipe_loader.load(env, filename)
    for recipe in recipes:
      values = recipe.steps[0].resolve_values({}, env)
      tarball_address = values.get('tarball_address')
      if tarball_address:
        tarball_address_address = tarball_address.address
        old_revision = tarball_address.revision
        gr = repo(temp_file.make_temp_dir(), address = tarball_address_address)
        gr.clone()
        new_revision = gr.last_commit_hash(short_hash = True)
        if old_revision == new_revision:
          return 0
        replacements = { old_revision: new_revision }
        print('%s: update %s -> %s' % (filename, old_revision, new_revision))
        file_replace.replace(filename, replacements, backup = False, word_boundary = True)
    return 0
      
if __name__ == '__main__':
  update_cli.run()
