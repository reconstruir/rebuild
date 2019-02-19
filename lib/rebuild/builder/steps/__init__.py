#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

###import pkgutil, sys
###_steps_path = sys.modules['rebuild.builder.steps'].__path__
###for _, modname, _ in pkgutil.iter_modules(path = _steps_path):
###  _source = 'from .%s import *' % (modname)
###  _code = compile(_source, __file__, 'exec')
###  print('CACA: %s' % (_source))
###  exec(_code, globals(), locals())

from .step_abort import *
from .step_artifact_create import *
from .step_autoconf import *
from .step_check_darwin_archs import *
from .step_check_hard_coded_paths import *
from .step_cleanup import *
from .step_cleanup_binary_filenames import *
from .step_cleanup_droppings import *
from .step_cleanup_gnu_info import *
from .step_cleanup_library_filenames import *
from .step_cleanup_libtool_droppings import *
from .step_cleanup_linux_fix_rpath import *
from .step_cleanup_macos_fix_rpath import *
from .step_cleanup_pkg_config_pcs import *
from .step_cleanup_python_droppings import *
from .step_cleanup_strip_binaries import *
from .step_cmake import *
from .step_combine_packages import *
from .step_install_delete_files import *
from .step_install_env_files import *
from .step_install_install_files import *
from .step_install_post_install_hooks import *
from .step_make import *
from .step_make_instructions import *
from .step_no_build import *
from .step_noop import *
from .step_perl_module import *
from .step_pkg_config_make_pc import *
from .step_post_install import *
from .step_python_egg import *
from .step_python_lib import *
from .step_python_standalone_program import *
from .step_run_script import *
from .step_setup import *
from .step_setup_ingest_upstream_sources import *
from .step_setup_install_requirements import *
from .step_setup_install_tool_requirements import *
from .step_setup_patch import *
from .step_setup_post_setup_hook import *
from .step_setup_post_unpack_hook import *
from .step_setup_prepare_environment import *
from .step_setup_sources_download import *
from .step_setup_sources_unpack import *
from .step_shell import *
from .step_xcodebuild import *
