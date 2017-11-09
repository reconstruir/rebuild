#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from bes.common import string_util
from bes.text import tree_text_parser

from rebuild.base import build_version
from rebuild.package_manager import package_descriptor

class recipe_parser_error(Exception):
  def __init__(self, message, filename, line_number):
    super(recipe_parser_error, self).__init__()
    self.message = message
    self.filename = filename
    self.line_number = line_number

  def __str__(self):
    if not self.line_number:
      return '%s: %s' % (self.filename, self.msg)
    else:
      return '%s:%s: %s' % (self.filename, self.line_number, self.msg)
    
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
  
  def _parse_package(self, pkg_node):
    name, version = self._parse_package_header(pkg_node)
    print('   name: %s' % (name))
    print('version: %s' % (str(version)))
    return None

  def _parse_package_header(self, pkg_node):
    parts = string_util.split_by_white_space(pkg_node.data.text, strip = True)
    if len(parts) != 2:
      self._error('package section should begin with \"package $name-$ver-$rev\"', pkg_node)
    if parts[0] != 'package':
      self._error('package section should begin with \"package $name-$ver-$rev\"', pkg_node)
    desc = package_descriptor.parse(parts[1])
    return desc.name, desc.version
  
  @classmethod
  def _node_is_comment(clazz, node):
    return node.data.text.startswith('#')

  
