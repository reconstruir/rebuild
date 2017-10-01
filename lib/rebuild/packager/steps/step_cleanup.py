#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import multiple_steps

from .step_cleanup_droppings import step_cleanup_droppings
from .step_cleanup_gnu_info import step_cleanup_gnu_info
from .step_cleanup_library_filenames import step_cleanup_library_filenames
from .step_cleanup_binary_filenames import step_cleanup_binary_filenames
from .step_cleanup_libtool_droppings import step_cleanup_libtool_droppings
from .step_cleanup_pkg_config_pcs import step_cleanup_pkg_config_pcs
from .step_cleanup_python_droppings import step_cleanup_python_droppings
from .step_cleanup_strip_binaries import step_cleanup_strip_binaries

class step_cleanup(multiple_steps):
  'A collection of multiple cleanup steps.'
  step_classes = [
    step_cleanup_droppings,
    step_cleanup_gnu_info,
    step_cleanup_library_filenames,
    step_cleanup_binary_filenames,
    step_cleanup_libtool_droppings,
    step_cleanup_pkg_config_pcs,
    step_cleanup_python_droppings,
    step_cleanup_strip_binaries,
  ]
  def __init__(self):
    super(step_cleanup, self).__init__()
