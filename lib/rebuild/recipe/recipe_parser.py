#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common import check_type, string_util
from bes.compat import StringIO
from bes.key_value import key_value_parser
from bes.system import log
from bes.text import tree_text_parser

from rebuild.base import build_version, masked_config, requirement, package_descriptor
from rebuild.step_manager import step_description
from .recipe import recipe
from .recipe_parser_util import recipe_parser_util
from .recipe_step import recipe_step
from .recipe_step_value import recipe_step_value
from .recipe_step_value_list import recipe_step_value_list

class recipe_parser_error(Exception):
  def __init__(self, message, filename, line_number):
    super(recipe_parser_error, self).__init__()
    self.message = message
    self.filename = filename
    self.line_number = line_number

  def __str__(self):
    if not self.line_number:
      return '%s: %s' % (self.filename, self.message)
    else:
      return '%s:%s: %s' % (self.filename, self.line_number, self.message)
    
class recipe_parser(object):

  MAGIC = '#!rebuildrecipe'

  def __init__(self, text, filename):
    self.text = text
    self.filename = filename

  def _error(self, msg, pkg_node = None):
    if pkg_node:
      line_number = pkg_node.data.line_number
    else:
      line_number = None
    raise recipe_parser_error(msg, self.filename, line_number)
    
  def parse(self):
    if not self.text.startswith(self.MAGIC):
      self._error('text should start with recipe magic \"%s\"' % (self.MAGIC))
    tree = tree_text_parser.parse(self.text)
    return self._parse_tree(tree)

  def _parse_tree(self, root):
    recipes = []
    for pkg_node in root.children:
      if self._node_is_comment(pkg_node):
        continue
      recipe = self._parse_package(pkg_node)
      recipes.append(recipe)
    return recipes
  
  def _parse_package(self, node):
    name, version = self._parse_package_header(node)
    enabled = True
    properties = {}
    requirements = []
    build_requirements = []
    build_requirements = []
    steps = []
    instructions = []
    for child in node.children:
      text = child.data.text
      if text.startswith('properties'):
        properties = self._parse_properties(child)
      elif text.startswith('requirements'):
        requirements = self._parse_requirements(child)
      elif text.startswith('build_requirements'):
        build_requirements = self._parse_requirements(child)
      elif text.startswith('steps'):
        steps = self._parse_steps(child)
    desc = package_descriptor(name, version, requirements = requirements,
                              build_requirements = build_requirements,
                              properties = properties)
    return recipe(self.filename, True, properties, requirements, build_requirements, 
                  desc, instructions, steps)

  def _parse_package_header(self, node):
    parts = string_util.split_by_white_space(node.data.text, strip = True)
    if len(parts) != 2:
      self._error('package section should begin with \"package $name-$ver-$rev\"', node)
    if parts[0] != 'package':
      self._error('package section should begin with \"package $name-$ver-$rev\"', node)
    desc = package_descriptor.parse(parts[1])
    return desc.name, desc.version
  
  def _parse_properties(self, node):
    properties = {}
    for child in node.children:
      property_text = self._node_text_recursive(child)
      values = key_value_parser.parse_to_dict(property_text, options = key_value_parser.KEEP_QUOTES)
      properties.update(values)
    return properties
  
  def _parse_requirements(self, node):
    reqs = []
    for child in node.children:
      req_text = self._node_text_recursive(child)
      next_reqs = requirement.parse(req_text)
      reqs.extend(next_reqs)
    return reqs

  def _parse_steps(self, node):
    steps = []
    for child in node.children:
      description = step_description.parse_description(child.data.text)
      step = self._parse_step(description, child)
      steps.append(step)
    return steps

  def _parse_step(self, description, node):
    name = node.data.text
    values = recipe_step_value_list()
    for child in node.children:
      more_values = self._parse_step_value(description, child)
      print('MORE_VALUES: %s - %d - %s' % (more_values, len(more_values), type(more_values)))
      assert isinstance(more_values, recipe_step_value_list)
      values.extend(more_values)
    return recipe_step(name, values)

  _data = namedtuple('_data', 'clazz,argspec')
  def _parse_step_value(self, description, node):
    result = recipe_step_value_list()
    arg_name = recipe_parser_util.parse_key(node.data.text)
    if not arg_name in description.argspec:
      self._error('invalid config \"%s\" instead of: %s' % (arg_name, ' '.join(description.argspec.keys())))
    value = recipe_step_value.parse_key_and_value(node.data.text, description.argspec[arg_name])
    if value.value:
      assert not node.children
      result.append(value)
    else:
      assert node.children
      for child in node.children:
        text = self._node_text_recursive(child)
        value = recipe_step_value.parse_mask_and_value(arg_name, text, description.argspec[arg_name])
        result.append(value)
    return result

  @classmethod
  def _node_is_comment(clazz, node):
    return node.data.text.startswith('#')

  @classmethod
  def _node_text_recursive(clazz, node):
    buf = StringIO()
    clazz._node_text_collect(node, ' ', buf)
    return buf.getvalue()

  @classmethod
  def _node_text_collect(clazz, node, delimiter, buf):
    buf.write(node.data.text)
    if node.children:
      buf.write(delimiter)
    for i, child in enumerate(node.children):
      clazz._node_text_collect(child, delimiter, buf)
      buf.write(delimiter)
