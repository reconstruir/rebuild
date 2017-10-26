#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

#from bes.system import log
from bes.common import check_type #algorithm, object_util
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

  _loaded_script = namedtuple('_loaded_script', 'filename,source_dir,recipe,source_dir,properties,requirements,build_requirements,descriptor,instructions,steps')

  @classmethod
  def load(clazz, filename, rebuild_env):
    load_env = build_script_load_env(build_target)
    recipes = clazz._load_recipes(filename, load_env)
    scripts = []
    for recipe in recipes.recipes:
      check_type.check_dict(recipe, 'recipe')
      script = clazz._load_from_dict(recipe)
      scripts.append(script)
    return scripts
  
  @classmethod
  def _load_from_factory_func(clazz, factory_func, load_env):
    assert callable(factory_func)
    args = copy.deepcopy(factory_func(load_env))
    clazz._load_from_dict(args)

  @classmethod
  def _load_from_recipe(clazz, recipe):
    
    
  @classmethod
  def _load_from_dict(clazz, args):
    properties = clazz._load_properties(args)
    name = properties.get('name', None)
    if not name:
      raise RuntimeError('No name given in %s.' % (clazz.filename))
    version = properties.get('version', None)
    if not version:
      raise RuntimeError('No version given in %s.' % (clazz.filename))
    del properties['name']
    del properties['version']
    requirements = clazz._load_requirements(args, 'requirements')
    build_requirements = clazz._load_requirements(args, 'build_requirements')
    
    # Check that some important properties are given
    if not package_descriptor.PROPERTY_CATEGORY in properties:
      raise RuntimeError('\"%s\" property missing from %s' % (package_descriptor.PROPERTY_CATEGORY, clazz.filename))
    clazz.package_descriptor = package_descriptor(name, version,
                                                 requirements = requirements,
                                                 build_requirements = build_requirements,
                                                 properties = properties)
    clazz.instruction_list = clazz._load_instructions(args, 'instructions')
    clazz.steps = clazz._load_steps(args)
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
