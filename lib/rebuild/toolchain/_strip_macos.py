#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ._strip_base import _strip_base

from rebuild import binary_format_macho
from rebuild.toolchain import toolchain
from bes.common import Shell

class _strip_macos(_strip_base):

  @classmethod
  def strip(clazz, build_target, binary):
    clazz.check_strippable(binary)
    macho = binary_format_macho()
    file_type = macho.file_type(binary)
    if not file_type:
      raise RuntimeError('not a valid binary: %s' % (binary))
    tc = toolchain.get_toolchain(build_target)
    ce = tc.compiler_environment()
    strip_exe = ce['STRIP']
    cmd = [ strip_exe ]
    if file_type == macho.FILE_TYPE_SHARED_LIB:
      cmd.append('-x')
    cmd.append(binary)
    rv = Shell.execute(cmd, raise_error = False)
    return rv.exit_code == 0
