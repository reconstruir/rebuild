#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import os

from bes.common.check import check

from .recipe_cli_command import recipe_cli_command

class recipe_cli_args(object):

  def __init__(self):
    pass
  
  def recipe_add_args(self, subparser):

    default_where = os.getcwd()
    
    # create
    p = subparser.add_parser('find', help = 'Find recipes.')
    p.add_argument('where', action = 'store', default = [ default_where ], nargs = '*',
                   help = 'Where to look for recipes. [ {} ]'.format(default_where))
    
  def _command_find(self, where):
    return recipe_cli_command.find(where)
