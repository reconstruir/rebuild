#!/usr/bin/env python
#-*- coding:utf-8 -*-

from ._strip_base import _strip_base

from rebuild.toolchain import toolchain
from bes.common import Shell

class _strip_linux(_strip_base):

  @classmethod
  def strip(clazz, build_target, binary):
    clazz.check_strippable(binary)
    ce = toolchain.compiler_environment(build_target)
    strip_exe = ce['STRIP']
    cmd = [ strip_exe, binary ]
    rv = Shell.execute(cmd, raise_error = False)
    return rv.exit_code == 0
