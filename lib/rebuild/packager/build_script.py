#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.system import log
from bes.common import algorithm
from rebuild import build_blurb
from rebuild.dependency import dependency_provider
from rebuild.step_manager import step_description, step_manager
from bes.fs import file_checksum

from .build_recipe_loader import build_recipe_loader

class build_script(object):

  def __init__(self, filename):
    log.add_logging(self, 'build')
    build_blurb.add_blurb(self, 'build')

    self.filename = filename
    self.source_dir = path.dirname(self.filename)
    self._step_manager = step_manager('build')

  def add_steps(self, packager_env):
    if self._step_manager.has_steps:
      raise RuntimeError('Script already has steps.')
    try:
      self._step_manager.add_steps(self.steps, packager_env)
    except Exception as ex:
      print(('Caught exception loading script: %s' % (self.filename)))
      raise

  def step_list(self, args):
    return self._step_manager.step_list(args)

  def execute(self, packager_env, args):
    result = self._step_manager.execute(packager_env, args)
    if result.success:
      packager_env.rebuild_env.checksum_manager.save_checksums(self._current_checksums(packager_env.rebuild_env.script_manager.scripts),
                                                               self.descriptor,
                                                               packager_env.rebuild_env.config.build_target)
    return result
        
  @property
  def disabled(self):
    return self.descriptor.disabled

  @property
  def sources(self):
    return self._script_sources()

  file_checksums = namedtuple('file_checksums', 'sources,targets')

  def _script_sources(self):
    'Return a list of sources for this script.'
    sources = []
    for step, args in self.step_list({}):
      for sources_key in step.sources_keys():
        if sources_key in args:
          assert isinstance(args[sources_key], list)
          sources.extend(args[sources_key])
      for k, v in args.items():
        sources.extend(dependency_provider.determine_provided(v))
    sources.append(self.filename)
    return sorted(algorithm.unique(sources))

  def _dep_sources(self, all_scripts):
    'Return a list of dependency sources for this script.'
    if not all_scripts:
      print('WEIRD a build script with no all_scripts: %s' % (self.filename))
      return []
    sources = []
    for dep in self.descriptor.requirements:
      dep_script = all_scripts[dep.name]
      sources += dep_script._sources(all_scripts)
    return sources

  def _sources(self, all_scripts):
    'Return a list of all script and dependency sources for this script.'
#    for f in self._script_sources():
#      print('%s: %s' % (self.descriptor.full_name, f))
    return self._script_sources() + self._dep_sources(all_scripts)

  def _targets(self):
    targets = []
    for step, args in self.step_list({}):
      if 'output_artifact_path' in args:
        targets.append(args['output_artifact_path'])
    return targets

  def _current_checksums(self, all_scripts):
    return self.file_checksums(file_checksum.checksums(self._sources(all_scripts)),
                               file_checksum.checksums(self._targets()))

  def needs_rebuilding(self, packager_env):
    rebuild_env = packager_env.rebuild_env
    try:
      loaded_checksums = rebuild_env.checksum_manager.load_checksums(self.descriptor,
                                                                     rebuild_env.config.build_target)
      
      # If the stored checksums don't match the current checksums, then we 
      if loaded_checksums:
        loaded_source_filenames = file_checksum.filenames(loaded_checksums.sources)
        loaded_target_filenames = file_checksum.filenames(loaded_checksums.targets)
#        for f in loaded_source_filenames:
#          self.blurb('%s CACA LOADED SOURCE: %s' % (self.descriptor.full_name, path.relpath(f)))
#        for f in loaded_target_filenames:
#          self.blurb('%s CACA LOADED TARGET: %s' % (self.descriptor.full_name, path.relpath(f)))
        current_checksums = self._current_checksums(rebuild_env.script_manager.scripts)
        current_source_filenames = file_checksum.filenames(current_checksums.sources)
        current_target_filenames = file_checksum.filenames(current_checksums.targets)
#        for f in current_source_filenames:
#          self.blurb('%s CACA CURRENT SOURCE: %s' % (self.descriptor.full_name, path.relpath(f)))
#        for f in current_target_filenames:
#          self.blurb('%s CACA CURRENT TARGET: %s' % (self.descriptor.full_name, path.relpath(f)))
        if current_source_filenames != current_source_filenames:
#          self.blurb('%s needs rebuilding because loaded and current source filenames are different.')
          return True

        if loaded_target_filenames != current_target_filenames:
          return True
          
      if not loaded_checksums:
        return True
      if not file_checksum.verify(loaded_checksums.sources):
        return True
      return False
    except IOError as ex:
      return True

  @classmethod
  def load_build_scripts(clazz, filename, build_target):
    recipes = build_recipe_loader.load(filename, build_target)
    scripts = []
    for recipe in recipes:
      script = build_script(recipe.filename)
      script.properties = recipe.properties
      script.requirements = recipe.requirements
      script.build_requirements = recipe.build_requirements
      script.descriptor = recipe.descriptor
      script.instructions = recipe.instructions
      script.steps = recipe.steps
      scripts.append(script)
    return scripts
