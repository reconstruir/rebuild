#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from rebuild.builder.builder_recipe_loader import builder_recipe_loader
from bes.git import repo
from bes.fs import file_replace, temp_file

def main():
  filename = path.abspath('build.py')
  r = builder_recipe_loader.load(filename)
  tarball_address = r[0].steps[0].args['tarball_address']
  address = tarball_address[0]
  tag = tarball_address[1]
  gr = repo(temp_file.make_temp_dir(), address = address)
  gr.clone()
  last = gr.last_commit_hash(short_hash = True)
  if last == tag:
    return 0
  replacements = { tag: last }
  print('%s: update %s -> %s' % (filename, tag, last))
  file_replace.replace(filename, replacements, backup = True, word_boundary = True)
  return 0

main()
