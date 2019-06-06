#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os.path as path
from bes.common.check import check
from bes.common.string_util import string_util
from bes.system import log
from bes.text import text_line_parser, tree_text_parser

from rebuild.recipe import recipe_error, recipe_parser_util
from rebuild.recipe.value import masked_value_list
from rebuild.recipe.variable_manager import variable_manager
from rebuild.base import requirement_list
from rebuild.config import storage_config_manager

from .venv_project_config import venv_project_config
from .venv_project_config_list import venv_project_config_list

class venv_project_config_parser(object):

  def __init__(self, filename, text, starting_line_number = 0):
    log.add_logging(self, 'venv_project_config_parser')
    self.text = text
    self.filename = filename
    self.starting_line_number = starting_line_number

  def _error(self, msg, pkg_node = None):
    if pkg_node:
      line_number = pkg_node.data.line_number + self.starting_line_number
    else:
      line_number = None
    lp = text_line_parser(self.text)
    lp.annotate_line('-> ', '   ', line_number, index = 0)
    lp.add_line_numbers(delimiter = ': ')
    msg = '%s\n%s' % (msg, str(lp))
    raise recipe_error(msg, self.filename, line_number)
    
  def parse(self, variable_manager):
    check.check_variable_manager(variable_manager)
    if not self.text.startswith(venv_project_config.MAGIC):
      first_line = self.text.split('\n')[0]
      self._error('text should start with recipe magic \"%s\" instead of \"%s\"' % (venv_project_config.MAGIC, first_line))
    try:
      tree = tree_text_parser.parse(self.text, strip_comments = True)
    except Exception as ex:
      self._error('failed to parse: %s' % (ex.message))
    return self._parse_tree(tree, variable_manager)

  _parse_result = namedtuple('_parse_result', 'projects, storage_config')
  def _parse_tree(self, root, variable_manager):
    if not root.children:
      self._error('invalid recipe', root)
    if root.children[0].data.text != venv_project_config.MAGIC:
      self._error('invalid magic', root)
    storage_config = None
    config_node = root.find_child_by_text('config')
    if config_node:
      storage_config = storage_config_manager(config_node, self.filename)
    projects = venv_project_config_list()
    root_projects_node = root.find_child_by_text('projects')
    for project_node in (root_projects_node.children or []):
      project = self._parse_project(project_node, variable_manager)
      projects.append(project)
    return self._parse_result(projects, storage_config)
  
  def _parse_project(self, node, variable_manager):
    name = self._parse_project_name(node)
    description = None
    variables = masked_value_list()
    packages = requirement_list()
    python_code = None

    # Need to deal with any inline python code first so its available for the rest of the recipe
    python_code_node = node.find_child(lambda child: child.data.text == 'python_code')
    if python_code_node:
      python_code = recipe_parser_util.parse_python_code(python_code_node, self.filename, self._error)

    for child in node.children:
      text = child.data.text
      if text.startswith('description'):
        description = recipe_parser_util.parse_description(child, self._error)
      elif text.startswith('variables'):
        variables.extend(recipe_parser_util.parse_masked_variables(child, self.filename))
      elif text.startswith('packages'):
        try:
          more_reqs = recipe_parser_util.parse_requirements(child, variable_manager)
        except ValueError as ex:
          self._error(str(ex), ex.child)
        dups = more_reqs.dups()
        if dups:
          self._error('duplicate package entries: %s' % (' '.join(dups)), child)
        packages.extend(more_reqs)
        dups = packages.dups()
        if dups:
          self._error('duplicate package entries: %s' % (' '.join(dups)), child)
      elif text.startswith('python_code'):
        # already dealth with up top
        pass
      else:
        self._error('unknown project section: \"%s\"' % (text), child)
    return venv_project_config(venv_project_config.FORMAT_VERSION,
                               self.filename,
                               name,
                               description,
                               variables,
                               packages,
                               python_code)

  def _parse_project_name(self, node):
    parts = string_util.split_by_white_space(node.data.text, strip = True)
    num_parts = len(parts)
    if num_parts not in [ 1 ]:
      self._error('project section should begin with \"project $name\" instead of \"%s\"' % (node.data.text), node)
    name = parts[0].strip()
    return name
