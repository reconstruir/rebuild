#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common import check, node
from bes.text import white_space
from bes.fs import file_util

from collections import namedtuple

from .fake_package_source import fake_package_source
from .fake_package_recipe_parser_util import fake_package_recipe_parser_util

class fake_package_binary_object(namedtuple('fake_package_binary_object', 'filename, sources, headers, ldflags')):
  'Class to describe fake source code for a package.'
  
  def __new__(clazz, filename, sources, headers, ldflags):
    check.check_string(filename)
    check.check_fake_package_source_seq(sources)
    check.check_fake_package_source_seq(headers)
    ldflags = ldflags or []
    check.check_string_seq(ldflags)
    return clazz.__bases__[0].__new__(clazz, filename, sources, headers, ldflags)

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
    if self.ldflags:
      ldflags_node = root.add_child('ldflags')
      for ldflag in self.ldflags:
        ldflag_node.children.append(ldflag)
    return root

  def compile(self, object):
    assert False

  _written_source = namedtuple('_written_source', 'filename, path, source_code')
  def write_files(self, where):
    sources = []
    headers = []
    root_dir = path.join(where, self.filename)

    for source in self.sources:
      p = source.write(root_dir)
      sources.append(self._written_source(source.filename, p, source.source_code))
      
    for header in self.headers:
      p = header.write(root_dir)
      headers.append(self._written_source(header.filename, p, header.source_code))
    
    return sources, headers

  @classmethod
  def parse_node(clazz, node):
    sources = []
    headers = []
    ldflags = []
    binary_object_filename = node.data.text
    sources_node = node.find_child_by_text('sources')
    if sources_node:
      for source_child in sources_node.children:
        source = fake_package_source.parse_node(source_child)
        sources.append(source)
    headers_node = node.find_child_by_text('headers')
    if headers_node:
      for header_child in headers_node.children:
        header = fake_package_source.parse_node(header_child)
        headers.append(header)
    ldflags_node = node.find_child_by_text('ldflags')
    if ldflags_node:
      ldflags = fake_package_recipe_parser_util.parse_node_children_to_string_list(ldflags_node)
    return fake_package_binary_object(node.data.text, sources, headers, ldflags)
  
  @classmethod
  def parse_node_children(clazz, node):
    return [ clazz.parse_node(child) for child in node.children ]
