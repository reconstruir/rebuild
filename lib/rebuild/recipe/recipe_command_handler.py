#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler
from bes.build.requirement_list import requirement_list
from bes.files.bf_file_ops import bf_file_ops
from bes.files.find.bf_file_finder import bf_file_finder

from rebuild.builder.builder_recipe_loader import builder_recipe_loader
from rebuild.recipe.recipe import recipe
from rebuild.recipe.recipe_load_env import testing_recipe_load_env

class recipe_command_handler(bcli_command_handler):

  def name(self):
    return 'recipe'

  def _command_find(self, where, options):
    for filename in self._find_recipes(where):
      print(filename)
    return 0

  def _command_fix_requirements_versions(self, where, python_version, options):
    recipe_filenames = self._find_recipes(where)
    recipes = self._load_recipes(recipe_filenames, python_version)
    for r in recipes.values():
      self._fix_one_requirements_versions(r, recipes)
    return 0

  def _fix_one_requirements_versions(self, r, other_recipes):
    new_requirements = requirement_list()
    for req in r.requirements:
      assert req.operator in [ '==', '>=' ]
      req_recipe = other_recipes[req.name]
      old_version = req.version
      new_version = req_recipe.upstream_version
      if old_version != new_version:
        new_req = req.clone(mutations = { 'version': new_version })
        new_requirements.append(new_req)
      else:
        new_requirements.append(req)
    if new_requirements != r.requirements:
      print('    FIX: {}: name={} old={} new={}'.format(r.filename, r.name, r.requirements, new_requirements))
      new_recipe = r.clone(mutations = { 'requirements': new_requirements })
      bf_file_ops.backup(new_recipe.filename)
      new_recipe.save_to_file(new_recipe.filename)

  def _find_recipes(self, where):
    finder = bf_file_finder()
    result = []
    for w in (where if isinstance(where, list) else [where]):
      result.extend(finder.find(w).entries.absolute_filenames())
    return sorted(f for f in result if self._is_recipe(f))

  def _is_recipe(self, filename):
    return recipe.is_recipe(filename) and not filename.lower().endswith('.bak')

  def _load_recipes(self, recipe_filenames, python_version):
    env = testing_recipe_load_env()
    env.variable_manager.add_variable('REBUILD_PYTHON_VERSION', python_version)
    result = {}
    for filename in recipe_filenames:
      recipes = builder_recipe_loader.load(env, filename)
      for r in recipes:
        name = r.descriptor.name
        if name in result:
          raise RuntimeError('duplicate recipe for "{}":\n  {}\n  {}'.format(name,
                                                                             r.filename,
                                                                             result[name].filename))
        result[name] = r
    return result
