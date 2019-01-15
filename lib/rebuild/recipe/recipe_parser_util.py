#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check, string_util
from bes.key_value import key_value
from bes.text import comments, string_list
from bes.system import logger

from rebuild.base import build_system, requirement_list

from .value import masked_value
from .value import masked_value_list
from .value import value_factory
from .value import value_key_values
from .value import value_origin
from .value import value_string_list

_LOG = logger('recipe_parser_util')

class recipe_parser_util(object):

  MASK_DELIMITER = ':'

  @classmethod
  def split_mask_and_value(clazz, s):
    mask, delimiter, value = s.partition(clazz.MASK_DELIMITER)
    if delimiter != clazz.MASK_DELIMITER:
      raise ValueError('no valid mask delimiter found: %s' % (s))
    return ( mask.strip(), value.strip() )
  
  @classmethod
  def strip_mask(clazz, s):
    _, value = clazz.split_mask_and_value(s)
    return value

  @classmethod
  def parse_key(clazz, origin, text):
    'Parse only the key'
    check.check_string(text)
    key, _, _ = comments.strip_line(text).partition(':')
    return key.strip()

  @classmethod
  def make_key_value(clazz, origin, text, node, value_class_name):
    check.check_value_origin(origin)
    check.check_string(text)
    check.check_node(node)
    check.check_string(value_class_name)
    text = comments.strip_line(text)
    key, delimiter, value = text.partition(':')
    key = key.strip()
    if not key:
      raise ValueError('%s: invalid step value key: \"%s\"' % (origin, text))
    if not delimiter:
      return key_value(key, None)
    value_text = value.strip() or None
    if not value_text:
      return key_value(key, None)
    value = value_factory.create_with_class_name(origin, value_text, node, value_class_name)
    return key_value(key, value)

  @classmethod
  def make_value(clazz, origin, text, node, value_class_name):
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    check.check_string(value_class_name)
    return value_factory.create_with_class_name(origin, text, node, value_class_name)

  @classmethod
  def make_value_caca(clazz, origin, text, node, value_class_name):
    if origin:
      check.check_value_origin(origin)
    check.check_node(node)
    check.check_string(value_class_name)
    return value_factory.create_with_class_name(origin, text, node, value_class_name)

  @classmethod
  def value_default(clazz, class_name):
    value_class = value_factory.get_class(class_name)
    return value_class.default_value(class_name)

  @classmethod
  def parse_python_code(clazz, node, filename, error_func):
    if node.data.text.strip() != 'python_code':
      error_func('python_code should be a string literal starting at line %d' % (node.data.line_number + 1), node)
    if len(node.children) != 1:
      error_func('python_code not found', node)
    code_node = node.children[0]
    # fill the top of the code with empty lines so that the python error line numbers
    # will match the line numbers in the recipe when compilation errors happen
    original_python_code = code_node.data.text
    filler_lines = '\n' * node.data.line_number
    filled_source_code = filler_lines + original_python_code
    c = compile(filled_source_code, filename, 'exec')
    exec_locals = {}
    exec(c, globals(), exec_locals)
    return original_python_code
  
  @classmethod
  def parse_masked_variables(clazz, node, filename):
    origin = value_origin(filename, node.data.line_number, node.data.text)
    values = value_key_values.xnew_parse(origin, node)
    return masked_value_list(values)
  
  @classmethod
  def parse_description(clazz, node, error_func):
    if len(node.children) == 0:
      error_func('description missing', node)
    return node.get_text(node.CHILDREN_INLINE, delimiter = '\n').strip()

  @classmethod
  def parse_requirements(clazz, node, variable_manager):
    reqs = []
    for child in node.children:
      req_text = child.get_text(child.NODE_FLAT)
      req_text = variable_manager.substitute(req_text)
      next_reqs = requirement_list.parse(req_text)
      reqs.extend(next_reqs)
    return requirement_list(reqs)
  
  @classmethod
  def parse_masked_list_of_lists(clazz, child, filename):
    origin = value_origin(filename, child.data.line_number, child.data.text)
    parts = string_util.split_by_white_space(child.data.text, strip = True)
    _LOG.log_d('parse_masked_list_child: parts=%s; \nchild=%s' % (parts, str(child)))
    result = []
    mask_valid = build_system.mask_is_valid(parts[0])
    if mask_valid:
      mask = parts.pop(0)
    else:
      mask = None
    _LOG.log_d('parse_masked_list_child: mask_valid=%s; mask=%s; parts=%s' % (mask_valid, mask, parts))
    if parts:
      result.append(masked_value(mask, value_string_list(origin = origin, value = parts), origin = origin))
    strings = child.get_text_children_as_string_list()
    _LOG.log_d('parse_masked_list_child: strings=%s' % (strings))
    values = [ masked_value(mask, value_string_list(origin = origin, value = [ s ]), origin = origin) for s in strings ]
    result.extend(values)
    return masked_value_list(result)
