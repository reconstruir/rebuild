#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import check_type

class recipe_parser_util(object):

  @classmethod
  def strip_comment(clazz, s):
    i = s.find('#')
    if i >= 0:
      return s[0:i]
    return s

  @classmethod
  def parse_key(clazz, text):
    'Parse only the key'
    check_type.check_string(text, 'text')
    key, _, _ = clazz.strip_comment(text).partition(':')
    return key.strip()
