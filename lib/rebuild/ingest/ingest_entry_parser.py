#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.check import check
from bes.common.string_util import string_util
from bes.system.log import log

from rebuild.recipe.recipe_data_manager import recipe_data_manager
from rebuild.recipe.recipe_parser_util import recipe_parser_util
from rebuild.recipe.value.masked_value_list import masked_value_list

from .ingest_download import ingest_download
from .ingest_entry import ingest_entry

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
    download = None
    
    for child in entry_node.children:
      text = child.data.text
      if text.startswith('description'):
        description = recipe_parser_util.parse_description(child, error_func)
      if text.startswith('data'):
        if not data:
          data = masked_value_list()
        data.extend(recipe_data_manager.parse_node(child, self.filename))
      elif text.startswith('variables'):
        if not variables:
          variables = masked_value_list()
        variables.extend(recipe_parser_util.parse_masked_variables(child, self.filename))
      elif text.startswith('download'):
        download = self._parse_download(child)

    return ingest_entry(name, version, description, data, variables, download)

  def _parse_header(self, node, error_func):
    parts = string_util.split_by_white_space(node.data.text, strip = True)
    if len(parts) != 3:
      error_func('invalid entry: {} - should be "entry $name $version"'.format(node.data.text))
    if parts[0].strip() != 'entry':
      error_func('invalid entry: {} - should be "entry $name $version"'.format(node.data.text))
    name = self.variable_manager.substitute(parts[1].strip())
    version = self.variable_manager.substitute(parts[2].strip())
    return name, version

  def _parse_download(self, node):
    url = None
    git = None
    for child in node.children:
      text = child.data.text
      if text.startswith('url'):
        if not url:
          url = masked_value_list()
        url.extend(recipe_parser_util.parse_masked_variables(child, self.filename))
      elif text.startswith('git'):
        if not git:
          git = masked_value_list()
        git.extend(recipe_parser_util.parse_masked_variables(child, self.filename))
    return ingest_download(url, git)
