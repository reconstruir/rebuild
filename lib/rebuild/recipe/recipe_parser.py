#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common import string_util
from bes.compat import StringIO
from bes.key_value import key_value_parser
from bes.system import log
from bes.text import tree_text_parser

from rebuild.base import build_version, masked_config, requirement
from rebuild.package_manager import package_descriptor
from rebuild.step_manager import step_description
from .recipe_step_value import recipe_step_value

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
    return recipe
  
  def _parse_package(self, node):
    name, version = self._parse_package_header(node)
    properties = {}
    requirements = []
    build_requirements = []
    build_requirements = []
    steps = []
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
    print('              name: %s' % (name))
    print('           version: %s' % (str(version)))
    print('        properties: %s' % (properties))
    print('      requirements: %s' % (requirements))
    print('build_requirements: %s' % (build_requirements))
    print('             steps: %s' % (steps))
    return None

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
      self._parse_step_section(description, child)
      #req_text = self._node_text_recursive(child)
      #next_reqs = requirement.parse(req_text)
      #reqs.extend(next_reqs)
    return steps

  def _parse_step_section(self, description, node):
    args = []
    print('_parse_step_section(node=%s)' % (node.data.text))
    for child in node.children:
      section_name = child.data.text
      self._parse_step_section_config(description, child)
      #next_reqs = requirement.parse(req_text)
      #reqs.extend(next_reqs)
    return args

  _data = namedtuple('_data', 'clazz,argspec')
  def _parse_step_section_config(self, description, node):
    arg_name = recipe_step_value.parse_key(node.data.text)
    if not arg_name in description.argspec:
      self._error('invalid config \"%s\" instead of: %s' % (arg_name), node, ' '.join(description.argspec.keys()))
    vk = recipe_step_value.parse(node.data.text, description.argspec[arg_name])
    configs = []
    if vk.value:
      mc = masked_config.parse(args_text)

    
    for child in node.children:
      args_text = self._node_text_recursive(child)
      mc = masked_config.parse(args_text)
      configs.append(mc)
    return configs

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
