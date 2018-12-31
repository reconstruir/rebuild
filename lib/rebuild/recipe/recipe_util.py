#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, node
from bes.text import text_line_parser, white_space

class recipe_util(object):

  @classmethod
  def python_code_to_node(clazz, python_code):
    result = node('python_code')
    parser = text_line_parser(python_code)
    first_line_text = '> ' + parser[0].text
    parser.prepend('  ' * 3)
    parser.replace_line_text(1, first_line_text)
    result.add_child(str(parser))
    return result

  @classmethod
  def variables_to_node(clazz, variables):
    variables_node = node('variables')
    for v in variables:
      variables_node.add_child(str(v))
    return variables_node
  
  @classmethod
  def description_to_node(clazz, description):
    result = node('description')
    parser = text_line_parser(description)
#    first_line_text = '> ' + parser[0].text
    parser.prepend('  ' * 3)
#    parser.replace_line_text(1, first_line_text)
    result.add_child(str(parser))
    return result

  @classmethod
  def root_node_to_string(clazz, node, depth = 0, indent = 2):
    s = node.to_string(depth = depth, indent = indent).strip()
    return white_space.shorten_multi_line_spaces(s)
