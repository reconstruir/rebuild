#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from instruction import instruction
from rebuild.recipe import recipe_section_parser

class instruction_list_parser(object):

  NAME_IDENTIFIER = 'name'
  REQUIRES_IDENTIFIER = 'requires'
  
  def __init__(self):
    pass
  
  def run(self, text):
    sections = recipe_section_parser.parse_to_list(text, self.NAME_IDENTIFIER)
    for section in sections:
      inst = self._parse_section(section)
      yield inst

  @classmethod
  def parse(clazz, text):
    return clazz().run(text)

  @classmethod
  def _parse_section(clazz, section):
    assert section.header.key == clazz.NAME_IDENTIFIER
    name = section.header.value
    requires_value = section.values.find_all_key(clazz.REQUIRES_IDENTIFIER)
    section.values.remove_key(clazz.REQUIRES_IDENTIFIER)
    requires = set()
    if requires_value:
      requires = set(requires_value[-1].value.split(' '))
    flags = section.values.to_dict()
    return instruction(name, flags, requires)
