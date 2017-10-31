#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.common import check_type
from bes.python import code

from rebuild import package_descriptor
from rebuild import instruction_list
from rebuild.hook_extra_code import HOOK_EXTRA_CODE
from rebuild.step_manager import step_description

from .build_recipe_env import build_recipe_env

class build_recipe_loader(object):

  _recipe = namedtuple('_recipe', 'filename,recipe,properties,requirements,build_requirements,descriptor,instructions,steps')

  @classmethod
  def load(clazz, filename, build_target):
    load_env = build_recipe_env(build_target)
    recipes = clazz._load_recipes(filename, load_env)
    scripts = []
    for recipe in recipes.recipes:
      check_type.check_dict(recipe, 'recipe')
      script = clazz._load_from_dict(recipe, filename)
      scripts.append(script)
    return scripts

  @classmethod
  def _load_from_dict(clazz, recipe, filename):
    properties = clazz._load_properties(recipe)
    name = properties.get('name', None)
    if not name:
      raise RuntimeError('No name given in %s.' % (filename))
    version = properties.get('version', None)
    if not version:
      raise RuntimeError('No version given in %s.' % (filename))
    del properties['name']
    del properties['version']
    requirements = clazz._load_requirements(recipe, 'requirements')
    build_requirements = clazz._load_requirements(recipe, 'build_requirements')
    
    # Check that some important properties are given
    if not package_descriptor.PROPERTY_CATEGORY in properties:
      raise RuntimeError('\"%s\" property missing from %s' % (package_descriptor.PROPERTY_CATEGORY, filename))
    descriptor = package_descriptor(name, version,
                                    requirements = requirements,
                                    build_requirements = build_requirements,
                                    properties = properties)
    instructions = clazz._load_instructions(recipe, 'instructions')
    steps = clazz._load_steps(recipe)
    if recipe:
      raise RuntimeError('Unknown recipe: %s' % (recipe))
    return clazz._recipe(filename, recipe, properties, requirements,
                         build_requirements, descriptor, instructions, steps)

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
    result = []
    for recipe in recipes:
      if callable(recipe):
        recipe = recipe(load_env)
      check_type.check_dict(recipe, 'recipe')
      result.append(recipe)
    return clazz._recipes(filename, result)
