#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os.path as path
from bes.fs import file_util, temp_item
from bes.common import check, string_util
from bes.compat import StringIO
from bes.key_value import key_value, key_value_list
from bes.text import string_list, tree_text_parser

from rebuild.base import build_version, requirement, requirement_list, package_descriptor
from rebuild.step.step_description import step_description
from rebuild.recipe.value import value_type
from rebuild.instruction import instruction_list

from .fake_package_recipe import fake_package_recipe
from .artifact_descriptor import artifact_descriptor

class fake_package_recipe_parser_error(Exception):
  def __init__(self, message, filename, line_number):
    super(fake_package_recipe_parser_error, self).__init__()
    self.message = message
    self.filename = filename
    self.line_number = line_number

  def __str__(self):
    if not self.line_number:
      return '%s: %s' % (self.filename, self.message)
    else:
      return '%s:%s: %s' % (self.filename, self.line_number, self.message)
    
class fake_package_recipe_parser(object):

  def __init__(self, filename, text, starting_line_number = 0):
    self.text = text
    self.filename = filename
    self.starting_line_number = starting_line_number

  def _error(self, msg, pkg_node = None):
    if pkg_node:
      line_number = pkg_node.data.line_number + self.starting_line_number
    else:
      line_number = None
    raise fake_package_recipe_parser_error(msg, self.filename, line_number)
    
  def parse(self):
    try:
      tree = tree_text_parser.parse(self.text, strip_comments = True)
    except Exception as ex:
      self._error('failed to parse: %s' % (ex.message))
    return self._parse_tree(tree)

  def _parse_tree(self, root):
    if not root.children:
      self._error('invalid recipe', root)
    recipes = []
    for pkg_node in root.children:
      recipe = self._parse_package(pkg_node)
      recipes.append(recipe)
    return recipes
  
  def _parse_package(self, node):
    if node.data.text != 'fake_package':
      self._error('invalid fake_package', node)
    metadata_node = node.find_child_by_text('metadata')
    if not metadata_node:
      self._error('no metadata found for fake_package', node)
    metadata = self._parse_metadata(metadata_node)
    files = []
    env_files = []
    requirements = []
    properties = {}
    files_node = node.find_child_by_text('files')
    if files_node:
      files = self._parse_files(files_node)
    env_files_node = node.find_child_by_text('env_files')
    if env_files_node:
      env_files = self._parse_files(env_files_node)
    return fake_package_recipe(metadata, files, env_files, requirements, properties)

  def _parse_metadata(self, node):
    d = self._parse_node_children_to_dict(node)
    name = d['name']
    version = d['version']
    revision = d['revision']
    epoch = d['epoch']
    system = d['system']
    level = d['level']
    arch = d['arch']
    distro = d['distro']
    distro_version = d['distro_version']
    return artifact_descriptor(name, version, revision, epoch,
                               system, level, arch, distro,
                               distro_version)

  def _parse_files(self, node):
    return [ self._parse_file(child) for child in node.children ]

  def _parse_file(self, node):
    filename = node.data.text
    content = '\n'.join(self._parse_node_children_to_string_list(node)) + '\n'
    if file_util.extension(filename) in [ 'sh', 'py' ]:
      mode = 0o755
    else:
      mode = 0o644
    return temp_item(filename, content, mode)

  @classmethod
  def _parse_node_children_to_dict(clazz, node):
    result = key_value_list()
    for child in node.children:
      result.append(key_value.parse(child.data.text))
    return result.to_dict()
  
  @classmethod
  def _parse_node_children_to_string_list(clazz, node):
    result = string_list()
    for child in node.children:
      result.append(child.data.text)
    return result
  
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

    value_class_name = args_definition[key].class_name
    value = recipe_parser_util.make_key_value(self.env, origin, node.data.text, value_class_name)
    if value.value:
      assert not node.children
      values.append(masked_value(None, value.value, origin))
    else:
      for child in node.children:
        text = tree_text_parser.node_text_flat(child)
        child_origin = value_origin(self.filename, child.data.line_number, text)
        try:
          value = masked_value.parse_mask_and_value(self.env, child_origin, text, value_class_name)
        except RuntimeError as ex:
          self._error('error: %s: %s - %s' % (origin, text, str(ex)), node)
        values.append(value)
    return recipe_value(key, values)
