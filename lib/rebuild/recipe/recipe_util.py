#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.node import node
from bes.text.text_line_parser import text_line_parser
from bes.text.white_space import white_space

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
  def variables_to_node(clazz, label, variables):
    return clazz.masked_value_list_to_node(label, variables)

  @classmethod
  def lines_to_node(clazz, label, lines):
    check.check_string(lines)
    result = node(label)
    for line in text_line_parser.parse_lines(lines, strip_comments = False, strip_text = True, remove_empties = True):
      result.add_child(line)
    return result
  
  @classmethod
  def masked_value_list_to_node(clazz, name, mvl):
    check.check_masked_value_list(mvl)
    result = node(name)
    for v in mvl:
      result.add_child(str(v))
    return result
  
  @classmethod
  def description_to_node(clazz, description):
    check.check_string(description)
    result = node('description')
    lines = text_line_parser.parse_lines(description, strip_comments = False, strip_text = False, remove_empties = False)
    for line in lines:
      result.add_child(line)
    return result

  @classmethod
  def root_node_to_string(clazz, node, depth = 0, indent = 2):
    s = node.to_string(depth = depth, indent = indent).strip()
    return white_space.shorten_multi_line_spaces(s)

  @classmethod
  def file_starts_with_magic(clazz, filename, magic):
    'Return True if filename starts with the given magic sequence.'
    magic = magic.encode('ascii')
    with open(filename, 'rb') as fin:
      try:
        return fin.read(len(magic)) == magic
      except IOError:
        return False
      except UnicodeDecodeError as ex:
        return False
  
  @classmethod
  def requirements_to_node(clazz, label, requirements):
    result = node(label)
    for req in requirements:
      result.add_child(req.to_string_colon_format())
    return result
