#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from rebuild.base import build_target, build_system
from rebuild.toolchain import compiler, toolchain, toolchain_testing
from bes.system import host
from bes.fs import file_util, temp_file
from bes.common.object_util import object_util
from bes.common.variable import variable
from bes.testing.unit_test.unit_test_skip import skip_if

CC_SOURCE = r'''
#include <stdio.h>
#include <limits.h>
int main(int argc, char* argv[])
{
  printf("%s::main()\n", __FILE__);
  return 0;
}
'''

CC_SOURCE = r'''
/* confdefs.h */
#define PACKAGE_NAME "libjpeg"
#define PACKAGE_TARNAME "libjpeg"
#define PACKAGE_VERSION "9.1.0"
#define PACKAGE_STRING "libjpeg 9.1.0"
#define PACKAGE_BUGREPORT ""
#define PACKAGE_URL ""
#define PACKAGE "libjpeg"
#define VERSION "9.1.0"
/* end confdefs.h.  */
#ifdef __STDC__
# include <limits.h>
#else
# include <assert.h>
#endif
'''

def _make_temp_source(tmp_dir, filename, content):
  return file_util.save(path.join(tmp_dir, filename), content = content)

def _make_compiler(system, arch):
  return compiler(build_target(system, '', '', arch, 'release'))

tmp_dir = temp_file.make_temp_dir()
src = _make_temp_source(tmp_dir, 'test.c', CC_SOURCE)
cc = _make_compiler(build_system.ANDROID, 'armv7')
targets = cc.compile_c(src)
assert len(targets) == 1
assert path.exists(targets[0][1])
print(targets)
