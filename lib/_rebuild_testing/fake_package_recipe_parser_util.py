#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.text import string_list
    
class fake_package_recipe_parser_util(object):

  @classmethod
  def parse_file(clazz, node):
    filename = node.data.text
    content = '\n'.join(clazz.parse_node_children_to_string_list(node)) + '\n'
    return filename, content

  @classmethod
  def parse_node_children_to_string_list(clazz, node):
    result = string_list()
    for child in node.children:
      result.append(child.data.text)
    return result
