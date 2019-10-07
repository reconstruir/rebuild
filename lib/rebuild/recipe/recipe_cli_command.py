#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#from bes.git.git_repo import git_repo
#from bes.archive.archiver import archiver
#from bes.archive.archive_util import archive_util

from bes.cli.cli_helper import cli_helper
from bes.fs.file_find import file_find

from rebuild.recipe.recipe import recipe

class recipe_cli_command(object):
  
  @classmethod
  def find(clazz, where):
    recipes = clazz._find_recipes(where)
    for r in recipes:
      print(r)
    return 0

  @classmethod
  def _find_recipes(clazz, where):
    return cli_helper.resolve_files(where, func = recipe.is_recipe)
