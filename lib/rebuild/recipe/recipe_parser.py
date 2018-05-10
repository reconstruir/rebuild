#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os.path as path
from bes.common import check, string_util
from bes.compat import StringIO
from bes.key_value import key_value, key_value_parser
from bes.system import log
from bes.text import string_list, tree_text_parser
from bes.python import code

from rebuild.base import build_version, requirement, requirement_list, package_descriptor
from rebuild.step.step_description import step_description
from rebuild.recipe.value import value_type
from rebuild.instruction import instruction_list

from .masked_value import masked_value
from .masked_value_list import masked_value_list

from .recipe import recipe
from .recipe_parser_util import recipe_parser_util
from .recipe_step import recipe_step
from .recipe_step_list import recipe_step_list
from .recipe_value import recipe_value

from .value import value_file
from .value import value_origin

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

  MAGIC = '!rebuild.recipe!'

  def __init__(self, env, filename, text, starting_line_number = 0):
    self.text = text
    self.env = env
    self.filename = filename
    self.starting_line_number = starting_line_number

  def _error(self, msg, pkg_node = None):
    if pkg_node:
      line_number = pkg_node.data.line_number + self.starting_line_number
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
        requirements.extend(self._parse_requirements(child))
      elif text.startswith('steps'):
        steps = self._parse_steps(child)
      elif text.startswith('source'):
        steps = self._parse_source(child)
      elif text.startswith('enabled'):
        enabled = self._parse_enabled(child)
      elif text.startswith('load'):
        load = self._parse_load(child)
        self._load_code(load, child)
      elif text.startswith('env_vars'):
        env_vars = self._parse_env_vars(child)
      elif text.startswith('instructions'):
        instructions = self._parse_instructions(child)
      elif text.startswith('export_compilation_flags_requirements'):
        export_compilation_flags_requirements = self._parse_export_compilation_flags_requirements(child)
        properties['export_compilation_flags_requirements'] = export_compilation_flags_requirements
      else:
        self._error('unknown recipe section: \"%s\"' % (text), node)
    if env_vars:
      poto1 = env_vars.resolve('macos', value_type.KEY_VALUES)
      poto2 = env_vars.resolve('linux', value_type.KEY_VALUES)
      d = poto1.to_dict()
      d.update(poto2.to_dict())
      properties['env_vars'] = d
    desc = package_descriptor(name, version, requirements = requirements, properties = properties)
    return recipe(2, self.filename, enabled, properties, requirements,
                  desc, instructions, steps, load, env_vars)

  def _parse_package_header(self, node):
    parts = string_util.split_by_white_space(node.data.text, strip = True)
    num_parts = len(parts)
    if num_parts not in [ 2, 3 ]:
      self._error('package section should begin with \"package $name $ver-$rev\" instead of \"%s\"' % (node.data.text), node)
    if parts[0] != 'package':
      self._error('package section should begin with \"package $name $ver-$rev\" instead of \"%s\"' % (node.data.text), node)
    if num_parts == 2:
      desc = package_descriptor.parse(parts[1])
      return desc.name, desc.version
    elif num_parts == 3:
      return parts[1], parts[2]
    else:
      assert False

  def _parse_enabled(self, node):
    enabled_text = tree_text_parser.node_text_flat(node)
    kv = key_value.parse(enabled_text, delimiter = '=')
    if kv.key != 'enabled':
      self._error('invalid "enabled" expression: %s' % (enabled_text))
    return kv.value
  
  def _parse_properties(self, node):
    properties = {}
    for child in node.children:
      property_text = tree_text_parser.node_text_flat(child)
      try:
        values = key_value_parser.parse_to_dict(property_text, options = key_value_parser.KEEP_QUOTES)
        properties.update(values)
      except RuntimeError as ex:
        self._error('error parsing properties: %s' % (property_text), node)
    return properties

  def _parse_source(self, node):
    source = {}
    for child in node.children:
#      property_text = tree_text_parser.node_text_flat(child)
      print('FUCK: child: %s' % (child))
#      try:
#        values = key_value_parser.parse_to_dict(property_text, options = key_value_parser.KEEP_QUOTES)
#        source.update(values)
#      except RuntimeError as ex:
#        self._error('error parsing source: %s' % (property_text), node)
    return source
  
  def _parse_requirements(self, node):
    reqs = []
    for child in node.children:
      req_text = tree_text_parser.node_text_flat(child)
      next_reqs = requirement_list.parse(req_text)
      reqs.extend(next_reqs)
    return requirement_list(reqs)

  def _parse_env_vars(self, node):
    env_vars = []
    for child in node.children:
      text = tree_text_parser.node_text_flat(child)
      child_origin = value_origin(self.filename, child.data.line_number, text)
      value = masked_value.parse_mask_and_value(self.env, child_origin, text, value_type.KEY_VALUES)
      env_vars.append(value)
    return masked_value_list(env_vars)

  def _parse_export_compilation_flags_requirements(self, node):
    export_compilation_flags_requirements = []
    for child in node.children:
      text = tree_text_parser.node_text_flat(child)
      child_origin = value_origin(self.filename, child.data.line_number, text)
      value = masked_value.parse_mask_and_value(self.env, child_origin, text, value_type.STRING_LIST)
      export_compilation_flags_requirements.append(value)
    return masked_value_list(export_compilation_flags_requirements)

  def _parse_instructions(self, node):
    text = tree_text_parser.node_text(node, include_root = False)
    return instruction_list.parse(text)

  def _parse_steps(self, node):
    steps = recipe_step_list()
    for child in node.children:
      try:
        description = step_description.parse_description(child.data.text)
      except RuntimeError as ex:
        self._error(ex.message)
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

#    recipe_file = value_file(env = self.env, filename = path.abspath(self.filename))
#    values.insert(0, recipe_value('recipe_filename', masked_value_list([ masked_value(None, recipe_file) ])))

    return recipe_step(name, description, values)

  def _parse_step_value(self, description, node):
    origin = value_origin(self.filename, node.data.line_number, node.data.text)
    values = masked_value_list()
    key = recipe_parser_util.parse_key(origin, node.data.text)
    args_definition = description.step_class.args_definition()
    if not key in args_definition:
      self._error('invalid config \"%s\" instead of: %s' % (key, ' '.join(args_definition.keys())), node)

    value_class_name = value_type.value_to_name(args_definition[key].atype).lower()
#    value = recipe_parser_util.parse_key_and_value(self.env, origin, node.data.text, args_definition[key].atype)
    value = recipe_parser_util.parse_key_and_value2(self.env, origin, node.data.text, value_class_name)
    if value.value:
      assert not node.children
      values.append(masked_value(None, value.value, origin))
    else:
      #      assert node.children
      for child in node.children:
        text = tree_text_parser.node_text_flat(child)
        child_origin = value_origin(self.filename, child.data.line_number, text)
        try:
          value = masked_value.parse_mask_and_value(self.env, child_origin, text, args_definition[key].atype)
        except RuntimeError as ex:
          self._error('error: %s: %s - %s' % (origin, text, str(ex)), node)
        values.append(value)
    return recipe_value(key, values)

  def _parse_load(self, node):
    loads = []
    for child in node.children:
      load_text = tree_text_parser.node_text_flat(child)
      next_loads = string_list.parse(load_text)
      loads.extend(next_loads)
    return loads

  def _load_code(self, loads, node):
    for l in loads:
      code_filename = path.join(path.dirname(self.filename), l)
      if not path.isfile(code_filename):
        self._error('python file to load not found: %s' % (code_filename), node)
      tmp_globals = {}
      tmp_locals = {}
      code.execfile(code_filename, tmp_globals, tmp_locals)
      for key, value in tmp_locals.items():
        if check.is_class(value):
          setattr(value, '__load_file__', code_filename)
