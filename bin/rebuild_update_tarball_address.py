#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.builder.builder_recipe_loader import builder_recipe_loader
from bes.git import repo
from bes.fs import file_replace, temp_file
from rebuild.base import build_system, build_target
from rebuild.recipe import recipe_load_env

def main():
  filename = path.abspath('rebuild.recipe')
  env = recipe_load_env(build_target(), None)
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

main()
