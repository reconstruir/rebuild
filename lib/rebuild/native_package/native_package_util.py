#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.algorithm import algorithm
from bes.text.text_line_parser import text_line_parser

class native_package_util(object):

  @classmethod
  def parse_lines(clazz, s, sort = False, unique = False):
    result = text_line_parser.parse_lines(s,
                                          strip_comments = False,
                                          strip_text = True,
                                          remove_empties = True)
    if sort:
      result = sorted(result)
    if unique:
      result = algorithm.unique(result)
    return result
