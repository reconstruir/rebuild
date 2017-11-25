#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import compound_step

from .step_cleanup_binary_filenames import step_cleanup_binary_filenames
from .step_cleanup_droppings import step_cleanup_droppings
from .step_cleanup_gnu_info import step_cleanup_gnu_info
from .step_cleanup_library_filenames import step_cleanup_library_filenames
from .step_cleanup_libtool_droppings import step_cleanup_libtool_droppings
from .step_cleanup_macos_fix_rpath import step_cleanup_macos_fix_rpath
from .step_cleanup_pkg_config_pcs import step_cleanup_pkg_config_pcs
from .step_cleanup_python_droppings import step_cleanup_python_droppings
from .step_cleanup_strip_binaries import step_cleanup_strip_binaries

class step_cleanup(compound_step):
  'A collection of multiple cleanup steps.'
  __steps__ = [
    step_cleanup_droppings,
    step_cleanup_gnu_info,
    step_cleanup_library_filenames,
    step_cleanup_binary_filenames,
    step_cleanup_libtool_droppings,
    step_cleanup_pkg_config_pcs,
    step_cleanup_python_droppings,
    step_cleanup_strip_binaries,
    step_cleanup_macos_fix_rpath,
  ]
  def __init__(self):
    super(step_cleanup, self).__init__()
