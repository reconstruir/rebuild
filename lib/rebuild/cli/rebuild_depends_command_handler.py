#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.bcli.bcli_command_handler import bcli_command_handler

from .rebuild_module_versions import rebuild_module_versions

class rebuild_depends_command_handler(bcli_command_handler):

  def name(self):
    return 'depends'

  def _command_versions(self, filenames, plain, options):
    versions = rebuild_module_versions.module_versions()
    print(rebuild_module_versions.format_module_versions(versions,
                                                         fancy = not plain,
                                                         filenames = filenames))
    return 0
