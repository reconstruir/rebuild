#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

#from bes.system import log
#from bes.common import algorithm, object_util
#from bes.fs import file_checksum
#from bes.python import code

#from rebuild import build_arch, build_type, package_descriptor
#from rebuild import build_blurb
#from rebuild import instruction_list
#from rebuild import platform_specific_config as psc
#from rebuild.dependency import dependency_provider
#from rebuild.hook_extra_code import HOOK_EXTRA_CODE
#from rebuild.step_manager import step_description, step_manager

from .build_script_env import build_script_env as build_script_load_env
#from .packager_env import packager_env

class build_script_loader(object):

  @classmethod
  def load(clazz, filename, rebuild_env):
    load_env = build_script_load_env(build_target)
    loaded_build_script = clazz.__load_recipes(filename, load_env)
    scripts = []
    for recipe in loaded_build_script.recipes:
      assert isinstance(recipe, dict)
      script = build_script(loaded_build_script.filename, rebuild_env)
      script.__load_from_dict(recipe)
      scripts.append(script)
    return scripts
  
  def _load_from_factory_func(self, factory_func, script_env):
    assert callable(factory_func)
    args = copy.deepcopy(factory_func(script_env))
    self._load_from_dict(args)

  def _load_from_dict(self, args):
    if not self.source_dir:
      if not 'source_dir' in args:
        raise RuntimeError('Not loading from a file and no source_dir given.')
      self.source_dir = args['source_dir']
      del args['source_dir']

    properties = self._load_properties(args)
    name = properties.get('name', None)
    if not name:
      raise RuntimeError('No name given in %s.' % (self.filename))
    version = properties.get('version', None)
    if not version:
      raise RuntimeError('No version given in %s.' % (self.filename))
    del properties['name']
    del properties['version']
    requirements = self._load_requirements(args, 'requirements')
    build_requirements = self._load_requirements(args, 'build_requirements')
    
    # Check that some important properties are given
    if not package_descriptor.PROPERTY_CATEGORY in properties:
      raise RuntimeError('\"%s\" property missing from %s' % (package_descriptor.PROPERTY_CATEGORY, self.filename))
    self.package_descriptor = package_descriptor(name, version,
                                                 requirements = requirements,
                                                 build_requirements = build_requirements,
                                                 properties = properties)
    self.instruction_list = self._load_instructions(args, 'instructions')
    self.steps = self._load_steps(args)
    if args:
      raise RuntimeError('Unknown args: %s' % (args))

  @classmethod
  def _load_requirements(clazz, args, key):
    if not key in args:
      return []
    requirements = package_descriptor.parse_requirements(args[key])
    del args[key]
    return requirements

  @classmethod
  def _load_instructions(clazz, args, key):
    if not key in args:
      return []
    result = instruction_list.parse(args[key])
    del args[key]
    return result
  
  @classmethod
  def _load_steps(clazz, args):
    if not 'steps' in args:
      return []
    steps = step_description.parse_descriptions(args['steps'])
    del args['steps']
    return steps

  @classmethod
  def _load_properties(clazz, args):
    if not 'properties' in args:
      return {}
    properties = args['properties']
    del args['properties']
    return properties

  _recipes = namedtuple('_recipes', 'filename,recipes')
  @classmethod
  def _load_recipes(clazz, filename, load_env):
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
    recipes = rebuild_recipes_func(load_env)
    if not isinstance(recipes, list):
      recipes = [ recipes ]
    loaded_recipes = []
    for recipe in recipes:
      if callable(recipe):
        recipe = recipe(load_env)
      elif not isinstance(recipe, dict):
        raise RuntimeError('Build recipe \"%s\" is not a dictionary: %s' % (recipe, filename))
      assert isinstance(recipe, dict)
      loaded_recipes.append(recipe)
    return clazz._recipes(filename, loaded_recipes)
