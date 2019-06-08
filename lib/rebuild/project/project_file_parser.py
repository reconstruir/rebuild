#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os.path as path
from bes.common.check import check
from bes.common.string_util import string_util
from bes.key_value.key_value_list import key_value_list
from bes.system.log import log
from bes.text.string_list import string_list
from bes.text.tree_text_parser import tree_text_parser
from bes.text.text_fit import text_fit

from rebuild.base.build_system import build_system
from rebuild.recipe.recipe_error import recipe_error
from rebuild.recipe.recipe_parser_util import recipe_parser_util
from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.value.value_origin import value_origin
from rebuild.recipe.value.value_string_list import value_string_list

from .project_file import project_file
from .project_file_list import project_file_list

class project_file_parser(object):

  def __init__(self, filename, text, starting_line_number = 0):
    log.add_logging(self, 'project_file_parser')
    self.text = text
    self.filename = filename
    self.starting_line_number = starting_line_number

  def _error(self, msg, pkg_node = None):
    if pkg_node:
      line_number = pkg_node.data.line_number + self.starting_line_number
    else:
      line_number = None
    raise recipe_error(msg, self.filename, line_number)
    
  def parse(self):
    if not self.text.startswith(project_file.MAGIC):
      first_line = self.text.split('\n')[0]
      self._error('text should start with recipe magic \"%s\" instead of \"%s\"' % (project_file.MAGIC, first_line))
    try:
      tree = tree_text_parser.parse(self.text, strip_comments = True)
    except Exception as ex:
      self._error('failed to parse: %s' % (ex.message))
    return project_file_list(self._parse_tree(tree))

  def _parse_tree(self, root):
    recipes = []
    if not root.children:
      self._error('invalid recipe', root)
    if root.children[0].data.text != project_file.MAGIC:
      self._error('invalid magic', root)
    for pkg_node in root.children[1:]:
      recipe = self._parse_project(pkg_node)
      recipes.append(recipe)
    return recipes
  
  def _parse_project(self, node):
    name = self._parse_project_name(node)
    description = None
    python_code = None
    variables = key_value_list()
    imports = masked_value_list()
    recipes = masked_value_list()

    # Need to deal with any inline python code first so its available for the rest of the recipe
    python_code_node = node.find_child(lambda child: child.data.text == 'python_code')
    if python_code_node:
      python_code = recipe_parser_util.parse_python_code(python_code_node, self.filename, self._error)

    for child in node.children:
      text = child.data.text
      if text.startswith('description'):
        description = recipe_parser_util.parse_description(child, self._error)
      elif text.startswith('variables'):
        variables.extend(self._parse_variables(child, self.filename))
      elif text.startswith('recipes'):
        recipes.extend(self._parse_masked_list(child))
      elif text.startswith('imports'):
        imports.extend(self._parse_masked_list(child))
      elif text.startswith('python_code'):
        # already dealth with up top
        pass
      else:
        self._error('unknown project section: \"%s\"' % (text), child)
    return project_file(project_file.FORMAT_VERSION,
                        self.filename,
                        name,
                        description,
                        variables,
                        imports,
                        recipes,
                        python_code)

  def _parse_project_name(self, node):
    parts = string_util.split_by_white_space(node.data.text, strip = True)
    num_parts = len(parts)
    if num_parts not in [ 2 ]:
      self._error('project section should begin with \"project $name\" instead of \"%s\"' % (node.data.text), node)
    if parts[0] != 'project':
      self._error('project section should begin with \"project $name\" instead of \"%s\"' % (node.data.text), node)
    name = parts[1].strip()
    return name

  def _parse_masked_list(self, node):
    #self.log_d('_parse_masked_list: filename=%s\nnode=%s' % (self.filename, str(node)))
    result = masked_value_list()
    for child in node.children:
      result.extend(self._parse_masked_list_child(child))
    return result

  def _parse_masked_list_child(self, child):
    origin = value_origin(self.filename, child.data.line_number, child.data.text)
    parts = string_util.split_by_white_space(child.data.text, strip = True)
    self.log_d('_parse_masked_list_child: parts=%s; \nchild=%s' % (parts, str(child)))
    result = []
    mask_valid = build_system.mask_is_valid(parts[0])
    if mask_valid:
      mask = parts.pop(0)
    else:
      mask = None
    self.log_d('_parse_masked_list_child: mask_valid=%s; mask=%s; parts=%s' % (mask_valid, mask, parts))
    if parts:
      result.append(masked_value(mask, value_string_list(origin = origin, value = parts), origin = origin))
    strings = self._node_get_string_list(child)
    self.log_d('_parse_masked_list_child: strings=%s' % (strings))
    values = [ masked_value(mask, value_string_list(origin = origin, value = [ s ]), origin = origin) for s in strings ]
    result.extend(values)
    return masked_value_list(result)

  
  @classmethod
  def _node_get_string_list(clazz, node):
    text = node.get_text(node.CHILDREN_FLAT)
    return string_util.split_by_white_space(text, strip = True)

  def _parse_variables(self, node, filename):
    #self.log_d('_parse_variables: filename=%s\nnode=%s' % (self.filename, str(node)))
    result = key_value_list()
    for child in node.children:
      result.extend(self._parse_variables_child(child))
    return result

  def _parse_variables_child(self, child):
    text = child.get_text(child.NODE_FLAT)
    return key_value_list.parse(text)
