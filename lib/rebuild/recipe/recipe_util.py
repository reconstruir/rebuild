#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, node
from bes.text import text_line_parser

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
  
