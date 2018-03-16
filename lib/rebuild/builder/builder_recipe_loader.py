#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os.path as path
from collections import namedtuple

from bes.common import check
from bes.python import code
from bes.fs import file_util

from rebuild.base import package_descriptor
from rebuild.instruction import instruction_list
from rebuild.step.hook_extra_code import HOOK_EXTRA_CODE
from rebuild.step import step_description
from rebuild.value import value_type
from rebuild.recipe import masked_value, masked_value_list, recipe, recipe_parser

from .builder_recipe_env import builder_recipe_env

class builder_recipe_loader(object):

  @classmethod
  def load(clazz, filename):
    load_env = builder_recipe_env()
    recipes = clazz._load_recipes(filename, load_env)
    if clazz._recipe_version(filename) == 2:
      return recipes.recipes
    result = []
    for recipe in recipes.recipes:
      check.check_dict(recipe)
      next_recipe = clazz._load_from_dict(recipe, filename)
      result.append(next_recipe)
    return result

  @classmethod
  def _load_from_dict(clazz, recipe_dict, filename):
    properties = clazz._load_properties(recipe_dict)
    enabled = clazz._load_enabled(recipe_dict)
    name = properties.get('name', None)
    if not name:
      raise RuntimeError('No name given in %s.' % (filename))
    version = properties.get('version', None)
    if not version:
      raise RuntimeError('No version given in %s.' % (filename))
    del properties['name']
    del properties['version']

#    requirements = clazz._load_requirements(recipe_dict, 'requirements')
    requirements = clazz._load_requirements_poto(recipe_dict, 'requirements')
    build_requirements = clazz._load_requirements(recipe_dict, 'build_requirements')
    build_tool_requirements = clazz._load_requirements(recipe_dict, 'build_tool_requirements')
    env_vars = clazz._load_env_vars(filename, recipe_dict, 'env_vars')
    if env_vars:
      pass
      #properties['env_vars'] = env_vars
      #resolved_env_vars = env_vars.resolve(self, system):
      #print('FUCK: LOADED env_vars[0]: %s - %s' % (str(env_vars[0]), type(env_vars[0])))
    
    # Check that some important properties are given
    if not package_descriptor.PROPERTY_CATEGORY in properties:
      raise RuntimeError('\"%s\" property missing from %s' % (package_descriptor.PROPERTY_CATEGORY, filename))
    descriptor = package_descriptor(name, version,
                                    requirements = requirements,
                                    build_requirements = build_requirements,
                                    build_tool_requirements = build_tool_requirements,
                                    properties = properties)
    instructions = clazz._load_instructions(recipe_dict, 'instructions')
    steps = clazz._load_steps(recipe_dict)
    # recipe_dict should be empty now
    if recipe_dict:
      raise RuntimeError('Unknown recipe values for %s: %s' % (filename, recipe_dict))
    return recipe(1, filename, enabled, properties, requirements, build_requirements,
                  build_tool_requirements, descriptor, instructions, steps, None, env_vars)

  @classmethod
  def _load_env_vars(clazz, filename, args, key):
    if not key in args:
      return []
    data = args[key]
    del args[key]
    assert isinstance(data, list)
    env_vars = []
    for text in data:
      value = masked_value.parse_mask_and_value(text, filename, value_type.KEY_VALUES)
      env_vars.append(value)
    return masked_value_list(env_vars)

  @classmethod
  def _load_requirements(clazz, args, key):
    if not key in args:
      return []
    requirements = package_descriptor.parse_requirements(args[key])
    del args[key]
    return requirements

  @classmethod
  def _load_requirements_poto(clazz, args, key):
    requirements = clazz._load_requirements(args, 'requirements')
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

  @classmethod
  def _load_enabled(clazz, args):
    if 'enabled' in args:
      enabled = args['enabled']
      del args['enabled']
    else:
      enabled = 'True'
    return enabled

  _recipes = namedtuple('_recipes', 'filename,recipes')
  @classmethod
  def _load_recipes_v1(clazz, filename, load_env):
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
      check.check_dict(recipe)
      result.append(recipe)
    return clazz._recipes(filename, result)

  @classmethod
  def _load_recipes_v2(clazz, filename):
    parser = recipe_parser(file_util.read(filename, codec = 'utf8'), filename)
    recipes = parser.parse()
    return clazz._recipes(filename, recipes)
  
  @classmethod
  def _load_recipes(clazz, filename, load_env):
    version =  clazz._recipe_version(filename)
    assert version in [ 1, 2]
    if version == 1:
      return clazz._load_recipes_v1(filename, load_env)
    else:
      return clazz._load_recipes_v2(filename)
  
  @classmethod
  def _recipe_version(clazz, filename):
    with open(filename, 'r') as fin:
      magic = fin.read(len(recipe_parser.MAGIC))
      if magic == recipe_parser.MAGIC:
        return 2
    return 1
