#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.cli.bes_application import bes_application

from rebuild.ingest.ingest_command_factory import ingest_command_factory
from rebuild.recipe.recipe_command_factory import recipe_command_factory

from .rebuild_depends_command_factory import rebuild_depends_command_factory

class rebuild_application(bes_application):

  #@abstractmethod
  def name(self):
    return 'rebuild'

  #@abstractmethod
  def parser_factories(self):
    return super().parser_factories() + [
      ingest_command_factory,
      recipe_command_factory,
      rebuild_depends_command_factory,
    ]
