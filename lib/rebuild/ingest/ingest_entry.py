#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.common.check import check
from bes.common.node import node
from bes.common.string_util import string_util
from bes.key_value.key_value_list import key_value_list
from bes.system.log import log

from rebuild.recipe.recipe_data_manager import recipe_data_manager
from rebuild.recipe.recipe_error import recipe_error
from rebuild.recipe.recipe_parser_util import recipe_parser_util
from rebuild.recipe.recipe_util import recipe_util
from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list

class ingest_download(namedtuple('ingest_download', 'url, git')):
  def __new__(clazz, url, git):
    check.check_masked_value_list(url, allow_none = True)
    check.check_masked_value_list(git, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, url, git)
check.register_class(ingest_download, include_seq = False)

class ingest_entry(namedtuple('ingest_entry', 'name, version, description, data, variables, download')):

  def __new__(clazz, name, version, description, data, variables, download):
    check.check_string(name)
    check.check_string(version)
    check.check_string(description, allow_none = True)
    check.check_masked_value_list(data, allow_none = True)
    check.check_masked_value_list(variables, allow_none = True)
    check.check_ingest_download(download, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, name, version, description, data, variables, download)

  def __str__(self):
    return self.to_string()

  def to_string(self, depth = 0, indent = 2):
    return recipe_util.root_node_to_string(self.to_node(), depth = depth, indent = indent)
  
  def to_node(self):
    root = node('entry {} {}'.format(self.name, self.version))
    if self.description:
      root.children.append(recipe_util.description_to_node(self.description))
      root.add_child('')
    if self.data:
      root.children.append(recipe_util.variables_to_node('data', self.data))
      root.add_child('')
    if self.variables:
      root.children.append(recipe_util.variables_to_node('variables', self.variables))
      root.add_child('')
    if self.download:
      root.children.append(self._download_to_node(self.download))
      root.add_child('')
    return root

  @classmethod
  def _download_to_node(clazz, download):
    download_node = node('download')
    if download.url:
      download_node.children.append(recipe_util.variables_to_node('url', download.url))
    if download.git:
      download_node.children.append(recipe_util.variables_to_node('git', download.git))
    return download_node
  
  @classmethod
  def parse(clazz, filename, variable_manager, node):
    check.check_string(filename)
    check.check_node(node)
    parser = ingest_entry_parser(filename, node, variable_manager)
    return parser.parse()

  def resolve_variables(self, system):
    if not self.variables:
      return key_value_list()
    return self.variables.resolve(system, 'key_values')
  
check.register_class(ingest_entry)

class ingest_entry_parser(object):

  def __init__(self, filename, node, variable_manager):
    log.add_logging(self, 'ingest_entry_parser')
    check.check_string(filename)
    check.check_node(node)
    self.filename = filename
    self.node = node
    self.variable_manager = variable_manager

  def _error(self, msg, pkg_node = None):
    if pkg_node:
      line_number = pkg_node.data.line_number
    else:
      line_number = None
    raise recipe_error(msg, self.filename, line_number)

  def parse(self):
    return self._parse_root()
    if not root.children:
      self._error('invalid recipe', root)
    if root.children[0].data.text != ingest_file.MAGIC:
      self._error('invalid magic', root)
    for pkg_node in root.children[1:]:
      recipe = self._parse_project(pkg_node)
      recipes.append(recipe)
    return recipes

  def _parse_root(self):
    if not self.node.children:
      self._error('invalid entry', self.node)
    entry_node = self.node.children[0]
    name, version = self._parse_header(self.node.children[0])
    description = None
    data = None
    variables = None
    download = None
    
    for child in entry_node.children:
      text = child.data.text
      if text.startswith('description'):
        description = recipe_parser_util.parse_description(child, self._error)
      if text.startswith('data'):
        if not data:
          data = masked_value_list()
        data.extend(recipe_data_manager.parse_node(child, self.filename))
      elif text.startswith('variables'):
        if not variables:
          variables = masked_value_list()
        variables.extend(recipe_parser_util.parse_masked_variables(child, self.filename))
      elif text.startswith('download'):
        download = self._parse_download(child)

    return ingest_entry(name, version, description, data, variables, download)

  def _parse_header(self, node):
    parts = string_util.split_by_white_space(node.data.text, strip = True)
    if len(parts) != 3:
      self._error('invalid entry: {} - should be "entry $name $version"'.format(node.data.text))
    if parts[0].strip() != 'entry':
      self._error('invalid entry: {} - should be "entry $name $version"'.format(node.data.text))
    name = self.variable_manager.substitute(parts[1].strip())
    version = self.variable_manager.substitute(parts[2].strip())
    return name, version

  def _parse_download(self, node):
    url = None
    git = None
    for child in node.children:
      text = child.data.text
      if text.startswith('url'):
        if not url:
          url = masked_value_list()
        url.extend(recipe_parser_util.parse_masked_variables(child, self.filename))
      elif text.startswith('git'):
        if not git:
          git = masked_value_list()
        git.extend(recipe_parser_util.parse_masked_variables(child, self.filename))
    return ingest_download(url, git)
