#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common import check, node
from bes.text import white_space

class fake_package_binary_object(namedtuple('fake_package_binary_object', 'filename, sources, headers')):
  'Class to describe fake source code for a package.'
  
  def __new__(clazz, filename, sources, headers):
    check.check_string(filename)
    check.check_fake_package_source_seq(sources)
    check.check_fake_package_source_seq(headers)
    return clazz.__bases__[0].__new__(clazz, filename, sources, headers)

  def __str__(self):
    return self.to_string()

  def to_string(self, depth = 0, indent = 2):
    s = self._to_node().to_string(depth = depth, indent = indent).strip()
    return white_space.shorten_multi_line_spaces(s)
  
  def _to_node(self):
    'A convenient way to make a string is to build a graph first.'
    root = node(self.filename)
    if self.sources:
      sources_node = root.add_child('sources')
      for source in self.sources:
        sources_node.children.append(source.to_node())
    if self.headers:
      headers_node = root.add_child('headers')
      for source in self.headers:
        headers_node.children.append(source.to_node())
    return root

  def compile(self, object):
    assert False
