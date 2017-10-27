#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path

#from bes.common import dict_util
from bes.system import log

from rebuild import build_blurb
from .packager_env import packager_env
from .build_script import build_script

TAG = 'packager'

class packager(object):
  
  def __init__(self, script, rebuild_env):
    log.add_logging(self, TAG)
    build_blurb.add_blurb(self, TAG)
#    file_util.mkdir(rebuild_env.config.build_dir)
    assert isinstance(script, build_script)

    #log.configure('software_packager=debug')

    self.script = script
    self.packager_env = packager_env(script, rebuild_env)
#    self._execute_args = copy.deepcopy(kargs)
#    self.blurb_verbose('execute_args:\n%s' % (dict_util.dumps(self._execute_args)))
    script.add_steps(self.packager_env)

  def execute(self):
    return self.script.execute(self.packager_env, {})#self._execute_args)
