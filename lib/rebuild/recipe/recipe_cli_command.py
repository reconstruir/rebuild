#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.cli_helper import cli_helper
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util

from rebuild.builder.builder_recipe_loader import builder_recipe_loader
from rebuild.recipe.recipe import recipe
from rebuild.recipe.recipe_load_env import testing_recipe_load_env
from bes.build.requirement_list import requirement_list

class recipe_cli_command(object):
  
  @classmethod
  def find(clazz, where):
    recipes = clazz._find_recipes(where)
    for r in recipes:
      print(r)
    return 0

  @classmethod
  def fix_requirements_versions(clazz, where, python_version):
    recipe_filenames = clazz._find_recipes(where)
    recipes = clazz._load_recipes(recipe_filenames, python_version)
    for recipe in recipes.values():
      clazz._fix_one_requirements_versions(recipe, recipes)
    return 0

  @classmethod
  def _fix_one_requirements_versions(clazz, recipe, other_recipes):
    new_requirements = requirement_list()
    for req in recipe.requirements:
      assert req.operator in [ '==', '>=' ]
      req_recipe = other_recipes[req.name]
      old_version = req.version
      new_version = req_recipe.upstream_version
      if old_version != new_version:
        new_req = req.clone(mutations = { 'version': new_version })
        new_requirements.append(new_req)
      else:
        new_requirements.append(req)
    if new_requirements != recipe.requirements:
      print('    FIX: {}: name={} old={} new={}'.format(recipe.filename, recipe.name, recipe.requirements, new_requirements))
      new_recipe = recipe.clone(mutations = { 'requirements': new_requirements })
      file_util.backup(new_recipe.filename)
      new_recipe.save_to_file(new_recipe.filename)
      
  @classmethod
  def _find_recipes(clazz, where):
    return cli_helper.resolve_files(where, func = clazz._is_recipe)

  @classmethod
  def _is_recipe(clazz, filename):
    return recipe.is_recipe(filename) and not filename.lower().endswith('.bak')

  @classmethod
  def _load_recipes(clazz, recipe_filenames, python_version):
    env = testing_recipe_load_env()
    env.variable_manager.add_variable('REBUILD_PYTHON_VERSION', python_version)
    result = {}
    for filename in recipe_filenames:
      recipes = builder_recipe_loader.load(env, filename)
      for recipe in recipes:
        name = recipe.descriptor.name
        if name in result:
          raise RuntimeError('duplicate recipe for "{}":\n  {}\n  {}'.format(name,
                                                                             recipe.filename,
                                                                             result[name].filename))
        result[name] = recipe
    return result
