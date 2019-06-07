#!/usr/bin/env python
#-*- coding:utf-8 -*-

from ._strip_base import _strip_base

from .toolchain import toolchain
from bes.system.execute import execute

class _strip_linux(_strip_base):

  @classmethod
  def strip(clazz, build_target, binary):
    clazz.check_strippable(binary)
    tc = toolchain.get_toolchain(build_target)
    ce = tc.compiler_environment()
    strip_exe = ce['STRIP']
    cmd = [ strip_exe, binary ]
    rv = execute.execute(cmd, raise_error = False)
    return rv.exit_code == 0
