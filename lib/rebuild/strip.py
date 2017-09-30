#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import Shell
from .toolchain import toolchain

class strip(object):

  @classmethod
  def strip(clazz, build_target, binaries):
    'Strip binaries.'
    if not binaries:
      return
    ce = toolchain.compiler_environment(build_target)
    strip_exe = ce['STRIP']
    for binary in binaries:
      cmd = '%s %s' % (strip_exe, binary)
      rv = Shell.execute(cmd, raise_error = False)
      if rv.exit_code != 0:
        print("FAILED TO STRIP: %s" % (binary))
