#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, os.path as path, platform
from abc import abstractmethod
from collections import namedtuple

from bes.common import dict_util
from bes.system import log
from bes.fs import file_checksum, file_util

from rebuild import build_blurb, build_target
from rebuild.step_manager import step_manager
from .packager_env import packager_env
from .build_script import build_script

TAG = 'packager'

class packager(object):
  
  def __init__(self, script, env, all_scripts, **kargs):
    log.add_logging(self, TAG)
    build_blurb.add_blurb(self, TAG)

    assert isinstance(script, build_script)

    #log.configure('software_packager=debug')

    tmp_dir = self.__tmp_dir(kargs)
    self.script = script
    self.packager_env = packager_env(script,
                                     env,
                                     all_scripts,
                                     tmp_dir,
                                     kargs.get('working_dir', None),
                                     kargs.get('rebbe_root', None))
    self.script.checksum_dir = path.join(env.checksum_manager.root_dir, env.config.build_target.build_path)
    self.script.all_scripts = all_scripts
    self._execute_args = copy.deepcopy(kargs)
    self.blurb_verbose('execute_args:\n%s' % (dict_util.dumps(self._execute_args)))
    script.add_steps(self.packager_env)

  @classmethod
  def __tmp_dir(clazz, args):
    tmp_dir = args.get('tmp_dir', None)
    assert tmp_dir
    file_util.mkdir(tmp_dir)
    return tmp_dir

  def execute(self):
    return self.script.execute(self.packager_env, self._execute_args)
