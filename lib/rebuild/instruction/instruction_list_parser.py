#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .instruction import instruction
from bes.text import string_list, tree_text_parser

class instruction_list_parser(object):

  REQUIRES = 'requires'
  
  def __init__(self):
    pass
  
  @classmethod
  def parse(clazz, text):
    tree = tree_text_parser.parse(text, strip_comments = True)
    return clazz._parse_tree(tree)

  @classmethod
  def _parse_tree(clazz, root):
    instructions = []
    for instruction_node in root.children:
      instruction = clazz._parse_instruction(instruction_node)
      instructions.append(instruction)
    return instructions

  @classmethod
  def _parse_instruction(clazz, node):
    name = node.data.text
    requires = None
    flags = {}
    for child in node.children:
      text = child.data.text
      if text == clazz.REQUIRES:
        requires = clazz._parse_requires(child)
      else:
        flag = clazz._parse_flag(child)
        flags.update(flag)
    return instruction(name, flags, requires)

  @classmethod
  def _parse_requires(clazz, node):
    assert node.data.text == clazz.REQUIRES
    text = tree_text_parser.node_children_text_flat(node)
    return string_list.parse(text).to_set()

  @classmethod
  def _parse_flag(clazz, node):
    key = node.data.text
    texts = []
    for child in node.children:
      texts.append(tree_text_parser.node_text_flat(child))
    value_text = ' '.join(texts)
    value = string_list.parse(value_text, options = string_list.KEEP_QUOTES)
    return { key: value }
