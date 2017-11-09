#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from bes.text import tree_text_parser

class recipe_parser(object):

  MAGIC = '#!rebuildrecipe'
  
  @classmethod
  def parse(clazz, text):
    if not text.startswith(clazz.MAGIC):
      raise ValueError('text should start with recipe magic \"%s\"' % (clazz.MAGIC))
    tree = tree_text_parser.parse(text)
    print(tree)
    return None
