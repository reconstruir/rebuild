#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.common import algorithm, object_util
from bes.python import code
from rebuild import build_arch, build_type, package_descriptor
from rebuild.dependency import dependency_provider
from rebuild.step_manager import step_description, step_manager
from bes.fs import file_checksum
from rebuild import platform_specific_config as psc
from .build_script_env import build_script_env
from rebuild.hook_extra_code import HOOK_EXTRA_CODE
from rebuild import instruction_list

class build_script(object):

  def __init__(self, filename):
    self.filename = filename
    self.source_dir = path.dirname(self.filename)
    self._step_manager = step_manager('build')

  def add_steps(self, packager_env):
    if self._step_manager.has_steps:
      raise RuntimeError('Script already has steps.')
    try:
      self._step_manager.add_steps(self.steps, packager_env)
      self._steps_added()
    except Exception as ex:
      print(('Caught exception loading script: %s' % (self.filename)))
      raise

  def step_list(self, args):
    return self._step_manager.step_list(args)

  def execute(self, packager_env, args):
    result = self._step_manager.execute(packager_env, args)
    if result.success:
      packager_env.rebuild_env.checksum_manager.save_checksums(self.__current_checksums(packager_env.rebuild_env.script_manager.scripts),
                                                               self.package_descriptor,
                                                               packager_env.rebuild_env.config.build_target)
    return result
        
  def __load_from_factory_func(self, factory_func, script_env):
    assert callable(factory_func)
    args = copy.deepcopy(factory_func(script_env))
    self.__load_from_dict(args)

  def __load_from_dict(self, args):
    if not self.source_dir:
      if not 'source_dir' in args:
        raise RuntimeError('Not loading from a file and no source_dir given.')
      self.source_dir = args['source_dir']
      del args['source_dir']

    properties = self.__load_properties(args)
    name = properties.get('name', None)
    if not name:
      raise RuntimeError('No name given in %s.' % (self.filename))
    version = properties.get('version', None)
    if not version:
      raise RuntimeError('No version given in %s.' % (self.filename))
    del properties['name']
    del properties['version']
    requirements = self.__load_requirements(args, 'requirements')
    build_requirements = self.__load_requirements(args, 'build_requirements')
    
    # Check that some important properties are given
    if not package_descriptor.PROPERTY_CATEGORY in properties:
      raise RuntimeError('\"%s\" property missing from %s' % (package_descriptor.PROPERTY_CATEGORY, self.filename))
    self.package_descriptor = package_descriptor(name, version,
                                                 requirements = requirements,
                                                 build_requirements = build_requirements,
                                                 properties = properties)
    self.instruction_list = self.__load_instructions(args, 'instructions')
    self.steps = self.__load_steps(args)
    if args:
      raise RuntimeError('Unknown args: %s' % (args))

  @classmethod
  def __load_requirements(clazz, args, key):
    if not key in args:
      return []
    requirements = package_descriptor.parse_requirements(args[key])
    del args[key]
    return requirements

  @classmethod
  def __load_instructions(clazz, args, key):
    if not key in args:
      return []
    result = instruction_list.parse(args[key])
    del args[key]
    return result
  
  @classmethod
  def __load_steps(clazz, args):
    if not 'steps' in args:
      return []
    steps = step_description.parse_descriptions(args['steps'])
    del args['steps']
    return steps

  @classmethod
  def __load_properties(clazz, args):
    if not 'properties' in args:
      return {}
    properties = args['properties']
    del args['properties']
    return properties

  @property
  def disabled(self):
    return self.package_descriptor.disabled

  @property
  def sources(self):
    return self.__script_sources()

  file_checksums = namedtuple('file_checksums', 'sources,targets')

  def __script_sources(self):
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

  def __dep_sources(self, all_scripts):
    'Return a list of dependency sources for this script.'
    if not all_scripts:
      print('WEIRD a build script with no all_scripts: %s' % (self.filename))
      return []
    sources = []
    for dep in self.package_descriptor.requirements:
      dep_script = all_scripts[dep.name]
      sources += dep_script.__sources(all_scripts)
    return sources

  def __sources(self, all_scripts):
    'Return a list of all script and dependency sources for this script.'
#    for f in self.__script_sources():
#      print('%s: %s' % (self.package_descriptor.full_name, f))
    return self.__script_sources() + self.__dep_sources(all_scripts)

  def __targets(self):
    targets = []
    for step, args in self.step_list({}):
      if 'output_artifact_path' in args:
        targets.append(args['output_artifact_path'])
    return targets

  def __current_checksums(self, all_scripts):
    return self.file_checksums(file_checksum.checksums(self.__sources(all_scripts)),
                               file_checksum.checksums(self.__targets()))

  def needs_rebuilding(self, packager_env):
    rebuild_env = packager_env.rebuild_env
    try:
      loaded_checksums = rebuild_env.checksum_manager.load_checksums(self.package_descriptor,
                                                                     rebuild_env.config.build_target)
      
      # If the stored checksums don't match the current checksums, then we 
      if loaded_checksums:
        loaded_source_filenames = file_checksum.filenames(loaded_checksums.sources)
        loaded_target_filenames = file_checksum.filenames(loaded_checksums.targets)

        current_checksums = self.__current_checksums(rebuild_env.script_manager.scripts)
        current_source_filenames = file_checksum.filenames(current_checksums.sources)
        current_target_filenames = file_checksum.filenames(current_checksums.targets)
        
        if loaded_source_filenames != current_source_filenames:
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

  _loaded_build_script = namedtuple('_loaded_build_script', 'filename,recipes')
  @classmethod
  def __load_build_script_recipes(clazz, filename, script_env):
    filename = path.abspath(path.normpath(filename))
    if not path.isfile(filename):
      raise RuntimeError('Build script file not found: %s' % (filename))
    tmp_globals = {}
    tmp_locals = {}
    exec(HOOK_EXTRA_CODE, tmp_locals, tmp_globals)
    code.execfile(filename, tmp_globals, tmp_locals)
    assert 'rebuild_recipes' in tmp_locals
    rebuild_recipes_func = tmp_locals['rebuild_recipes']
    if not callable(rebuild_recipes_func):
      raise RuntimeError('Build recipe factory \"%s\" is not callable: %s' % (rebuild_recipes_func, filename))
    recipes = rebuild_recipes_func(script_env)
    if not isinstance(recipes, list):
      recipes = [ recipes ]
    loaded_recipes = []
    for recipe in recipes:
      if callable(recipe):
        recipe = recipe(script_env)
      elif not isinstance(recipe, dict):
        raise RuntimeError('Build recipe \"%s\" is not a dictionary: %s' % (recipe, filename))
      assert isinstance(recipe, dict)
      loaded_recipes.append(recipe)
    return clazz._loaded_build_script(filename, loaded_recipes)

  @classmethod
  def load_build_scripts(clazz, filename, build_target):
    script_env = build_script_env(build_target)
    loaded_build_script = clazz.__load_build_script_recipes(filename, script_env)
    scripts = []
    for recipe in loaded_build_script.recipes:
      assert isinstance(recipe, dict)
      script = build_script(loaded_build_script.filename)
      script.__load_from_dict(recipe)
      scripts.append(script)
    return scripts

  def _steps_added(self):
    'Do work that can happen only after the steps are added.'
    pass
