#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

class recipe_error(Exception):
  def __init__(self, message, filename, line_number):
    super(recipe_error, self).__init__()
    self.message = message
    self.filename = path.relpath(filename)
    self.line_number = line_number

  def __str__(self):
    if not self.line_number:
      return '%s: %s' % (self.filename, self.message)
    else:
      return '%s:%s: %s' % (self.filename, self.line_number, self.message)

  @classmethod
  def make_error(clazz, msg, filename, pkg_node = None, starting_line_number = 1):
    if pkg_node:
      line_number = pkg_node.data.line_number + starting_line_number
    else:
      line_number = None
    return recipe_error(msg, filename, line_number)
