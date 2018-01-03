#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os.path as path
from bes.common import check, string_util
from bes.compat import StringIO
from bes.key_value import key_value, key_value_parser
from bes.system import log
from bes.text import string_list_parser, tree_text_parser
from bes.python import code

from rebuild.base import build_version, masked_config, requirement, package_descriptor
from rebuild.step import step_description, step_arg_type

from .masked_value import masked_value
from .masked_value_list import masked_value_list
from .recipe import recipe
from .recipe_parser_util import recipe_parser_util
from .recipe_step import recipe_step
from .recipe_step_list import recipe_step_list
from .recipe_value import recipe_value

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

  MAGIC = '!rebuildrecipe!'

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
    tree = tree_text_parser.parse(self.text, strip_comments = True)
    return self._parse_tree(tree)

  def _parse_tree(self, root):
    recipes = []
    if not root.children:
      self._error('invalid recipe', root)
    if root.children[0].data.text != self.MAGIC:
      self._error('invalid magic', root)
    for pkg_node in root.children[1:]:
      recipe = self._parse_package(pkg_node)
      recipes.append(recipe)
    return recipes
  
  def _parse_package(self, node):
    name, version = self._parse_package_header(node)
    enabled = True
    properties = {}
    requirements = []
    build_requirements = []
    steps = []
    instructions = []
    enabled = 'True'
    load = []
    env_vars = None
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
      elif text.startswith('enabled'):
        enabled = self._parse_enabled(child)
      elif text.startswith('load'):
        load = self._parse_load(child)
        self._load_code(load, child)
      elif text.startswith('env_vars'):
        env_vars = self._parse_env_vars(child)
    desc = package_descriptor(name, version, requirements = requirements,
                              build_requirements = build_requirements,
                              properties = properties)
    return recipe(2, self.filename, enabled, properties, requirements, build_requirements, 
                  desc, instructions, steps, load, env_vars)

  def _parse_package_header(self, node):
    parts = string_util.split_by_white_space(node.data.text, strip = True)
    if len(parts) != 2:
      self._error('package section should begin with \"package $name-$ver-$rev\" instead of \"%s\"' % (node.data.text), node)
    if parts[0] != 'package':
      self._error('package section should begin with \"package $name-$ver-$rev\" instead of \"%s\"' % (node.data.text), node)
    desc = package_descriptor.parse(parts[1])
    return desc.name, desc.version

  def _parse_enabled(self, node):
    enabled_text = self._node_text_recursive(node)
    kv = key_value.parse(enabled_text, delimiter = '=')
    if kv.key != 'enabled':
      self._error('invalid "enabled" expression: %s' % (enabled_text))
    return kv.value
  
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

  def _parse_env_vars(self, node):
    env_vars = []
    for child in node.children:
      text = self._node_text_recursive(child)
      value = masked_value.parse_mask_and_value(text, self.filename, step_arg_type.KEY_VALUES)
      env_vars.append(value)
    return masked_value_list(env_vars)

  def _parse_steps(self, node):
    steps = recipe_step_list()
    for child in node.children:
      description = step_description.parse_description(child.data.text)
      step = self._parse_step(description, child)
      steps.append(step)
    return steps

  def _parse_step(self, description, node):
    name = node.data.text
    values = []
    for child in node.children:
      more_values = self._parse_step_value(description, child)
      assert isinstance(more_values, recipe_value)
      values.append(more_values)
    return recipe_step(name, description, values)

  def _parse_step_value(self, description, node):
    values = masked_value_list()
    key = recipe_parser_util.parse_key(node.data.text)
    args_definition = description.step_class.args_definition()
    if not key in args_definition:
      self._error('invalid config \"%s\" instead of: %s' % (key, ' '.join(args_definition.keys())))
    value = recipe_parser_util.parse_key_and_value(node.data.text, self.filename, args_definition[key].atype)
    if value.value:
      assert not node.children
      values.append(masked_value(None, value.value))
    else:
#      assert node.children
      for child in node.children:
        text = self._node_text_recursive(child)
        value = masked_value.parse_mask_and_value(text, self.filename, args_definition[key].atype)
        values.append(value)
    return recipe_value(key, values)

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

  def _parse_load(self, node):
    loads = []
    for child in node.children:
      load_text = self._node_text_recursive(child)
      next_loads = string_list_parser.parse_to_list(load_text)
      loads.extend(next_loads)
    return loads

  def _load_code(self, loads, node):
    for l in loads:
      filename = path.join(path.dirname(self.filename), l)
      if not path.isfile(filename):
        self._error('file not found: %s' % (filename), node)
      tmp_globals = {}
      tmp_locals = {}
      code.execfile(filename, tmp_globals, tmp_locals)
      for key, value in tmp_locals.items():
        if check.is_class(value):
          setattr(value, '__load_file__', filename)
