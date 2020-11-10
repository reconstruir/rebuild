#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_item
from bes.common.check import check
from bes.common.string_util import string_util
from bes.key_value.key_value import key_value
from bes.key_value.key_value_list import key_value_list
from bes.key_value.key_value_parser import key_value_parser
from bes.compat.StringIO import StringIO
from bes.text.string_list import string_list
from bes.text.tree_text_parser import tree_text_parser

from rebuild.base.artifact_descriptor import artifact_descriptor
from rebuild.base.requirement_list import requirement_list

from .fake_package_recipe import fake_package_recipe
from .fake_package_source import fake_package_source
from .fake_package_recipe_parser_util import fake_package_recipe_parser_util
from .fake_package_binary_object import fake_package_binary_object

class fake_package_recipe_error(Exception):
  def __init__(self, message, filename, line_number):
    super(fake_package_recipe_error, self).__init__()
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
    raise fake_package_recipe_error(msg, self.filename, line_number)
    
  def parse(self):
    try:
      # Need to hack newlines before and after because the parse will strip them
      text = string_util.replace(self.text, { '\\n': '@@@NL@@@' })
      tree = tree_text_parser.parse(text, strip_comments = True)
      tree.replace_text({ '@@@NL@@@': r'\\n' })
    except Exception as ex:
      self._error('failed to parse: {}\n{}\n'.format(ex.message, self.text))
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
    if not node.data.text.startswith('fake_package'):
      self._error('invalid fake_package', node)
    metadata = self._parse_metadata(node)
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
    requirements_node = node.find_child_by_text('requirements')
    if requirements_node:
      requirements = self._parse_requirements(requirements_node)
    properties_node = node.find_child_by_text('properties')
    if properties_node:
      properties = self._parse_properties(properties_node)
    objects = {}
    
    c_programs_node = node.find_child_by_text('c_programs')
    if c_programs_node:
      objects['c_programs'] = fake_package_binary_object.parse_node_children(c_programs_node)
      
    static_c_libs_node = node.find_child_by_text('static_c_libs')
    if static_c_libs_node:
      objects['static_c_libs'] = fake_package_binary_object.parse_node_children(static_c_libs_node)
      
    shared_c_libs_node = node.find_child_by_text('shared_c_libs')
    if shared_c_libs_node:
      objects['shared_c_libs'] = fake_package_binary_object.parse_node_children(shared_c_libs_node)
      
    return fake_package_recipe(metadata, files, env_files, requirements, properties, objects)

  def _parse_metadata(self, node):
    parts = string_util.split_by_white_space(node.data.text, strip = True)
    assert parts[0] == 'fake_package'
    parts.pop(0)
    if len(parts) != len(artifact_descriptor._fields):
      self._error('invalid metadata for fake_package: \"%s\"' % (' '.join(parts)), node)
    return artifact_descriptor(*parts)
  
  def _parse_files(self, node):
    return [ self._parse_file(child) for child in node.children ]

  def _parse_file(self, node):
    filename, content = fake_package_recipe_parser_util.parse_file(node)
    if file_util.extension(filename) in [ 'sh', 'py' ]:
      mode = 0o755
    else:
      mode = 0o644
    return temp_item(filename, content, mode)

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
