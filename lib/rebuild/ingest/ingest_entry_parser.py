#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.string_util import string_util
from bes.system.log import log

from rebuild.base.build_system import build_system
from rebuild.recipe.recipe_data_manager import recipe_data_manager
from rebuild.recipe.recipe_parser_util import recipe_parser_util
from rebuild.recipe.value.masked_value import masked_value
from rebuild.recipe.value.masked_value_list import masked_value_list
from rebuild.recipe.value.value_origin import value_origin
from rebuild.recipe.value.value_key_values import value_key_values
from rebuild.recipe.value.value_parsing import value_parsing
from bes.key_value.key_value_list import key_value_list

from .ingest_download import ingest_download
from .ingest_entry import ingest_entry

from .ingest_method_descriptor_download import ingest_method_descriptor_download
from .ingest_method_descriptor_git import ingest_method_descriptor_git
from .ingest_method import ingest_method

class ingest_entry_parser(object):

  def __init__(self, filename, variable_manager):
    log.add_logging(self, 'ingest_entry_parser')
    check.check_string(filename)
    self.filename = filename
    self.variable_manager = variable_manager

  def parse(self, entry_node, error_func):
    check.check_node(entry_node)
    if not entry_node.data.text.startswith('entry'):
      error_func('invalid entry', entry_node)
    name, version = self._parse_header(entry_node, error_func)
    description = None
    data = None
    variables = None
    method = None
    
    for child in entry_node.children:
      text = child.data.text
      if text.startswith('description'):
        description = recipe_parser_util.parse_description(child, error_func)
      if text.startswith('data'):
        if not data:
          data = masked_value_list()
        next_data = recipe_data_manager.parse_node(child, self.filename)
        print('next_data: {}'.format(next_data))
        data.extend(recipe_data_manager.parse_node(child, self.filename))
      elif text.startswith('variables'):
        if not variables:
          variables = masked_value_list()
        variables.extend(recipe_parser_util.parse_masked_variables(child, self.filename))
      elif text.startswith('method'):
        method = self._parse_method(child, error_func)

    return ingest_entry(name, version, description, data, variables, method)

  def _parse_header(self, node, error_func):
    parts = string_util.split_by_white_space(node.data.text, strip = True)
    if len(parts) != 3:
      error_func('invalid entry: {} - should be "entry $name $version"'.format(node.data.text))
    if parts[0].strip() != 'entry':
      error_func('invalid entry: {} - should be "entry $name $version"'.format(node.data.text))
    name = self.variable_manager.substitute(parts[1].strip())
    version = self.variable_manager.substitute(parts[2].strip())
    return name, version

  def _parse_method(self, node, error_func):
    text = node.data.text
    if not text.startswith('method'):
      error_func('invalid method header: {} - should be "method git|download"'.format(text))
    parts = string_util.split_by_white_space(text, strip = True)
    if len(parts) != 2:
      error_func('invalid method header: {} - should be "method git|download"'.format(text))
    if not text.startswith('method'):
      error_func('invalid method header: {} - should be "method git|download"'.format(text))
    method = parts[1]
    desc = None
    if method == 'git':
      desc = ingest_method_descriptor_git()
    elif method == 'download':
      desc = ingest_method_descriptor_download()
    else:
      error_func('invalid method: {} - should be one of: git download'.format(method))
    values = self._parse_masked_key_values_children(node, error_func)
    keys = set()
    for v in values:
      for kv in v.value:
        keys.add(kv.key)
    required_keys = desc.required_field_keys()
    missing_keys = required_keys - keys
    if missing_keys:
      error_func('method "{}" missing the following fields: {}'.format(method, ' '.join(missing_keys)))
    return ingest_method(method, values)

  def _parse_masked_key_values_children(self, node, error_func):
    #self.log_d('_parse_masked_key_values_children: filename=%s\nnode=%s' % (self.filename, str(node)))
    result = masked_value_list()
    for child in node.children:
      result.extend(self._parse_masked_key_values_node(child, error_func))
    return result

  def _parse_masked_key_values_node(self, node, error_func):
    origin = value_origin(self.filename, node.data.line_number, node.data.text)
    text = node.get_text(node.NODE_FLAT)
    mav = value_parsing.split_mask_and_value(origin, text)
    result = []
    if not build_system.mask_is_valid(mav.mask):
      error_func('invalid system mask: {}"'.format(mav.mask))
    self.log_d('_parse_masked_key_values_node: mask={}; value={}'.format(mav.mask, mav.value))
    key_values = key_value_list.parse(mav.value)
    result.append(masked_value(mav.mask, value_key_values(origin = origin, value = key_values), origin = origin))
    return masked_value_list(result)
  
