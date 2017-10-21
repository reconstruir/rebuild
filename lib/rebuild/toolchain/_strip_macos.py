#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ._strip_base import _strip_base

import os
from rebuild import binary_detector, binary_format_macho
from rebuild.toolchain import toolchain
from bes.common import Shell
from bes.fs import file_util

class _strip_macos(_strip_base):

  @classmethod
  def strip(clazz, build_target, binary):
    macho = binary_format_macho()
    file_type = macho.file_type(binary)
    if not file_type:
      raise RuntimeError('not a valid binary: %s' % (binary))
    if not binary_detector.is_strippable(binary):
      raise RuntimeError('not a strippable binary: %s' % (binary))
    ce = toolchain.compiler_environment(build_target)
    strip_exe = ce['STRIP']
    cmd = [ strip_exe ]
    if file_type == macho.FILE_TYPE_SHARED_LIB:
      cmd.append('-x')
    cmd.append(binary)

    save_mode = None
    if file_type == macho.FILE_TYPE_SHARED_LIB:
      save_mode = file_util.mode(binary)

    rv = Shell.execute(cmd, raise_error = False)
    result = rv.exit_code == 0
    if save_mode is not None:
      os.chmod(binary, save_mode)
    return result
