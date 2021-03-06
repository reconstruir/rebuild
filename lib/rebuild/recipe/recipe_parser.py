#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os.path as path
from bes.common import check, string_util
from bes.compat import StringIO
from bes.key_value import key_value, key_value_parser
from bes.system import log
from bes.text import string_list, tree_text_parser, text_fit
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
from .recipe_list import recipe_list

from .value import value_file
from .value import value_origin
from .value import value_factory

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

  def __init__(self, filename, text, starting_line_number = 0):
    self.text = text
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
    try:
      tree = tree_text_parser.parse(self.text, strip_comments = True)
    except Exception as ex:
      self._error('failed to parse: %s' % (ex.message))
    return recipe_list(self._parse_tree(tree))

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
    for child in node.children:
      text = child.data.text
      if text.startswith('properties'):
        properties = self._parse_properties(child)
      elif text.startswith('requirements'):
        requirements.extend(self._parse_requirements(child))
      elif text.startswith('steps'):
        steps = self._parse_steps(child)
      elif text.startswith('enabled'):
        enabled = self._parse_enabled(child)
      elif text.startswith('load'):
        load = self._parse_load(child)
        self._load_code(load, child)
      elif text.startswith('instructions'):
        instructions = self._parse_instructions(child)
      elif text.startswith('export_compilation_flags_requirements'):
        export_compilation_flags_requirements = self._parse_export_compilation_flags_requirements(child)
        properties['export_compilation_flags_requirements'] = export_compilation_flags_requirements
      else:
        self._error('unknown recipe section: \"%s\"' % (text), node)
    desc = package_descriptor(name, version, requirements = requirements, properties = properties)
    return recipe(2, self.filename, enabled, properties, requirements,
                  desc, instructions, steps, load)

  def _parse_package_header(self, node):
    parts = string_util.split_by_white_space(node.data.text, strip = True)
    num_parts = len(parts)
    if num_parts not in [ 3, 4 ]:
      self._error('package section should begin with \"package $name $ver $rev\" instead of \"%s\"' % (node.data.text), node)
    if parts[0] != 'package':
      self._error('package section should begin with \"package $name $ver $rev\" instead of \"%s\"' % (node.data.text), node)
    if num_parts == 3:
      name = parts[1].strip()
      version = build_version.parse(parts[2])
      return name, version
    elif num_parts == 4:
      name = parts[1].strip()
      version = build_version.parse(parts[2])
      if version.revision != 0:
        self._error('revision given multiple times: %s' % (node.data.text), node)
      revision = parts[3].strip()
      return name, build_version(version.upstream_version, revision, version.epoch)

  def _parse_enabled(self, node):
    enabled_text = node.get_text(node.NODE_FLAT)
    kv = key_value.parse(enabled_text, delimiter = '=')
    if kv.key != 'enabled':
      self._error('invalid "enabled" expression: %s' % (enabled_text))
    return kv.value
  
  def _parse_properties(self, node):
    properties = {}
    for child in node.children:
      property_text = child.get_text(child.NODE_FLAT)
      try:
        values = key_value_parser.parse_to_dict(property_text, options = key_value_parser.KEEP_QUOTES)
        properties.update(values)
      except RuntimeError as ex:
        self._error('error parsing properties: %s' % (property_text), node)
    return properties

  def _parse_requirements(self, node):
    reqs = []
    for child in node.children:
      req_text = child.get_text(child.NODE_FLAT)
      next_reqs = requirement_list.parse(req_text)
      reqs.extend(next_reqs)
    return requirement_list(reqs)

  def _parse_export_compilation_flags_requirements(self, node):
    export_compilation_flags_requirements = []
    for child in node.children:
      text = child.get_text(child.NODE_FLAT)
      child_origin = value_origin(self.filename, child.data.line_number, text)
      value = self._caca_parse_mask_and_value(child_origin, text, child, value_type.STRING_LIST)
      export_compilation_flags_requirements.append(value)
    return masked_value_list(export_compilation_flags_requirements)

  def _parse_instructions(self, node):
    text = node.get_text(node.CHILDREN_INLINE)
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
    return recipe_step(name, description, values)

  def _parse_step_value(self, description, node):
    origin = value_origin(self.filename, node.data.line_number, node.data.text)
    values = masked_value_list()
    key = recipe_parser_util.parse_key(origin, node.data.text)
    args_definition = description.step_class.args_definition()
    if not key in args_definition:
      valid_configs_lines = text_fit.fit_text(' '.join(args_definition.keys()), 80)
      valid_configs_text = '\n    '.join(valid_configs_lines)
      self._error('invalid config \"%s\"\nvalid configs:\n    %s' % (key, valid_configs_text), node)

    value_class_name = args_definition[key].class_name
    value_class = value_factory.get_class(value_class_name)

    value = recipe_parser_util.make_key_value(origin, node.data.text, node, value_class_name)

    if False:
      if hasattr(value_class, 'new_parse'):
        new_value = value_class.new_parse(origin, node)
        print('CACA: new_value: %s' % (str(new_value)))
    
    if value.value:
      assert not node.children
      values.append(masked_value(None, value.value, origin))
    else:
      for child in node.children:
        text = child.get_text(child.NODE_FLAT)
        child_origin = value_origin(self.filename, child.data.line_number, text)
        try:
          value = self._caca_parse_mask_and_value(child_origin, text, child, value_class_name)
        except RuntimeError as ex:
          self._error('error: %s: %s - %s' % (origin, text, str(ex)), node)
        values.append(value)
    return recipe_value(key, values)

  def _parse_load(self, node):
    loads = []
    for child in node.children:
      load_text = child.get_text(child.NODE_FLAT)
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

  @classmethod
  def _caca_parse_mask_and_value(clazz, origin, text, node, class_name):
    check.check_value_origin(origin)
    check.check_string(text)
    check.check_node(node)
    check.check_string(class_name)
    mask, value = recipe_parser_util.split_mask_and_value(text)
    value = recipe_parser_util.make_value(origin, value, node, class_name)
    return masked_value(mask, value, origin)
          
