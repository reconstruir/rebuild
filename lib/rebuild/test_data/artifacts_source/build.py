#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os
from bes.fs import file_util
from rebuild.builder import *

publish_dir = '_artifacts'

class step_make_echo_script(Step):
  def __init__(self):
    super(step_make_echo_script, self).__init__()

  def execute(self, script, env, args):
    full_name = script.package_info.full_name
    content = '#!/bin/bash\necho %s\nexit 0\n' % (full_name)
    filename = '%s.sh' % (full_name)
    file_util.save(path.join(script.stage_dir, 'bin', filename), content = content, mode = 0755)
    return step_result(True, None)

steps = [
  step_shell, 'mkdir -p $REBUILD_STAGE_PREFIX_DIR',
  step_shell, 'cd $REBUILD_STAGE_PREFIX_DIR && mkdir -p bin lib include',
  step_shell, 'cd $REBUILD_STAGE_PREFIX_DIR && touch lib/libbar-$VERSION.a include/bar-$VERSION.h',
  step_make_echo_script,
  step_pkg_config_make_pc, [ '$NAME.pc' ],
  step_cleanup,
  step_artifact_create,
]

foo_123_1 = Script.args(name = 'foo', version = '1.2.3', revision = '1')
# FIXME: when this duplicate item is given the run code still works even though it clobbers an existsing dir
#foo_123_2 = Script.args(name = 'foo', version = '1.2.3', revision = '1')
foo_123_2 = Script.args(name = 'foo', version = '1.2.3', revision = '2')
foo_124_1 = Script.args(name = 'foo', version = '1.2.4', revision = '1')

bar_666_1 = Script.args(name = 'bar', version = '6.6.6', revision = '1')
bar_666_1 = Script.args(name = 'bar', version = '6.6.7', revision = '1')

baz_100_1 = Script.args(name = 'baz', version = '1.0.0', revision = '1')

packages = [
  foo_123_1,
  foo_123_2,
  foo_124_1,
  bar_666_1,
  bar_666_1,
  baz_100_1,
]

if __name__ == '__main__':
  file_util.remove( [ 'tmp', '_artifacts' ])
  for system in [ build_target.LINUX, build_target.MACOS ]:
    for args in packages:
      Script.run(exit_process = False,
                 system = system,
                 publish_dir = publish_dir,
                 steps = steps,
                 **args)
  file_util.remove('_artifacts/.git')
