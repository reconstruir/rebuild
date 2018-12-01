#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from bes.common import check
from bes.text import text_line_parser

class value_error(Exception):
  def __init__(self, message, filename, line_number, recipe_text):
    check.check_string(message)
    check.check_string(filename)
    check.check_int(line_number)
    check.check_string(recipe_text)
    super(value_error, self).__init__()
    self.message = message
    self.filename = filename
    self.line_number = line_number
    self.recipe_text = recipe_text

  def __str__(self):
    if self.recipe_text:
      lp = text_line_parser(self.recipe_text)
      if self.line_number:
        lp.annotate_line('-> ', '   ', self.line_number, index = 0)
      lp.add_line_numbers(delimiter = ': ')
      recipe_text = str(lp)
    else:
      recipe_text = None

    if recipe_text:
      message = '%s\n%s' % (self.message, recipe_text)
    else:
      message = self.message
      
    if not self.line_number:
      return '%s: %s' % (self.filename, message)
    else:
      return '%s:%s: %s' % (self.filename, self.line_number, message)

  @classmethod
  def raise_error(clazz, origin, msg, starting_line_number = None):
    starting_line_number = starting_line_number or 0
    check.check_value_origin(origin)
    check.check_string(msg)
    raise clazz(msg, origin.filename, origin.line_number + starting_line_number, origin.recipe_text)
    
