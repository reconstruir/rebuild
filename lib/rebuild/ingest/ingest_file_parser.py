#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os.path as path
from bes.common.check import check
from bes.key_value.key_value_list import key_value_list
from bes.fs.file_util import file_util
from bes.system.log import log
from bes.text.tree_text_parser import tree_text_parser

from rebuild.recipe.recipe_error import recipe_error
from rebuild.recipe.recipe_parser_util import recipe_parser_util

from .ingest_file import ingest_file
from .ingest_entry import ingest_entry
from .ingest_entry_parser import ingest_entry_parser
from .ingest_entry_list import ingest_entry_list

from rebuild.recipe.variable_manager import variable_manager

class ingest_file_parser(object):

  def __init__(self, filename, text, starting_line_number = 0):
    log.add_logging(self, 'ingest_file_parser')
    self.text = text
    self.filename = filename
    self.starting_line_number = starting_line_number

  def _error(self, msg, node = None):
    if node:
      line_number = node.data.line_number + self.starting_line_number
    else:
      line_number = None
    raise recipe_error(msg, self.filename, line_number)
    
  def parse(self):
    if not self.text.startswith(ingest_file.MAGIC):
      first_line = self.text.split('\n')[0]
      self._error('text should start with recipe magic \"%s\" instead of \"%s\"' % (ingest_file.MAGIC, first_line))
    try:
      tree = tree_text_parser.parse(self.text, strip_comments = True)
    except Exception as ex:
      self._error('failed to parse: %s' % (ex.message))
    return self._parse_tree(tree)

  def _parse_tree(self, root):
    # FIXME: need to figure out if variable_manager should be an argument
    vm = variable_manager()
    recipes = []
    if not root.children:
      self._error('invalid recipe', root)
    if root.children[0].data.text != ingest_file.MAGIC:
      self._error('invalid magic', root)

    description = None
    variables = key_value_list()
    entries = ingest_entry_list()

    for child in root.children[1:]:
      text = child.data.text
      if text.startswith('description'):
        description = recipe_parser_util.parse_description(child, self._error)
      elif text.startswith('variables'):
        variables.extend(self._parse_variables(child, self.filename))
      elif text.startswith('entry'):
        entry = ingest_entry_parser(self.filename, vm).parse(child, self._error)
        entries.append(entry)
        
    result = ingest_file(ingest_file.FORMAT_VERSION, self.filename,
                         description, variables, entries)
    for entry in entries:
      entry.ingest_file = result
    return result

  def _parse_variables(self, node, filename):
    #self.log_d('_parse_variables: filename=%s\nnode=%s' % (self.filename, str(node)))
    result = key_value_list()
    for child in node.children:
      result.extend(self._parse_variables_child(child))
    return result

  def _parse_variables_child(self, child):
    text = child.get_text(child.NODE_FLAT)
    return key_value_list.parse(text)

  @classmethod
  def parse_file(clazz, filename):
    content = file_util.read(filename, codec = 'utf8')
    return ingest_file_parser(filename, content).parse()
