#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_application import bcli_application

from bat.build.ingest.ingest_command_factory import ingest_command_factory
from rebuild.recipe.recipe_command_factory import recipe_command_factory

class retool_application(bcli_application):

  #@abstractmethod
  def name(self):
    return 'retool'

  #@abstractmethod
  def parser_factories(self):
    return [
      ingest_command_factory,
      recipe_command_factory,
    ]
