#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common.check import check
from bes.common.node import node
from bes.text.white_space import white_space
from bes.fs.file_util import file_util

from .fake_package_recipe_parser_util import fake_package_recipe_parser_util

class fake_package_source(namedtuple('fake_package_source', 'filename, source_code')):
  'Class to describe fake source code for a package.'
  
  def __new__(clazz, filename, source_code):
    check.check_string(filename)
    check.check_string(source_code)
    return clazz.__bases__[0].__new__(clazz, filename, source_code)

  def __str__(self):
    return self.to_string()

  def to_string(self, depth = 0, indent = 2):
    s = self.to_node().to_string(depth = depth, indent = indent).strip()
    return white_space.shorten_multi_line_spaces(s)
  
  def to_node(self):
    'A convenient way to make a string is to build a graph first.'
    root = node(self.filename)
    for line in self.source_code.split('\n'):
      root.add_child(line)
    return root

  @classmethod
  def parse_node(clazz, node):
    'Parse a fake_package_source from a recipe node.'
    filename, source_code = fake_package_recipe_parser_util.parse_file(node)
    return clazz(filename, source_code)
    
  def write(self, where):
    return file_util.save(path.join(where, self.filename), content = self.source_code)

check.register_class(fake_package_source)
