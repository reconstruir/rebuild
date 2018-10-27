#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from collections import namedtuple
from bes.common import check, node
from bes.text import white_space
#from bes.fs import file_util, temp_file

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

  def compile(self, object):
    assert False

check.register_class(fake_package_source)
