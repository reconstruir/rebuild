#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs import file_util, temp_item
from bes.common import check, string_util
from bes.key_value import key_value, key_value_list, key_value_parser
from bes.compat import StringIO
from bes.text import string_list, tree_text_parser

from rebuild.base import requirement_list
from rebuild.package import artifact_descriptor

from .fake_package_recipe import fake_package_recipe
from .fake_package_source import fake_package_source
from .fake_package_recipe_parser_util import fake_package_recipe_parser_util
from .fake_package_binary_object import fake_package_binary_object

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
    c_program_node = node.find_child_by_text('c_program')
    if c_program_node:
      c_programs = self._parse_binary_objects(c_program_node)
      print('FUCK: %s' % (str(c_programs)))
    return fake_package_recipe(metadata, files, env_files, requirements, properties)

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
    filename = node.data.text
    content = '\n'.join(self._parse_node_children_to_string_list(node)) + '\n'
    if file_util.extension(filename) in [ 'sh', 'py' ]:
      mode = 0o755
    else:
      mode = 0o644
    return temp_item(filename, content, mode)

  @classmethod
  def _parse_node_children_to_string_list(clazz, node):
    result = string_list()
    for child in node.children:
      result.append(child.data.text)
    return result
  
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

  def _parse_binary_objects(self, node):
    result = []
    for child in node.children:
      filename = child.data.text
      bo = self._parse_binary_object(child)
      result.append(bo)
    return result

  def _parse_binary_object(self, node):
    sources = []
    binary_object_filename = node.data.text
    sources_node = node.find_child_by_text('sources')
    if sources_node:
      for source_child in sources_node.children:
        source = fake_package_source.parse_node(source_child)
        sources.append(source)
    return fake_package_binary_object(node.data.text, sources, [])
