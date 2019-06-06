#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from rebuild.pkg_config import pkg_config

class test_pkg_config(unittest.TestCase):

  FOO_PC = '''prefix=/usr/foo
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
sharedlibdir=${libdir}
includedir=${prefix}/include

Name: foo
Description: foo library
Version: 1.2.3

Requires:
Libs: -L${libdir} -L${sharedlibdir} -lfoo
Cflags: -I${includedir} -DFOO
'''

  BAR_PC = '''prefix=/usr/bar
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
sharedlibdir=${libdir}
includedir=${prefix}/include

Name: bar
Description: bar library
Version: 1.2.3

Requires:
Libs: -L${libdir} -L${sharedlibdir} -lbar
Cflags: -I${includedir} -DBAR
'''

  FOO_DUP_PC = '''prefix=/usr/foo_dup
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
sharedlibdir=${libdir}
includedir=${prefix}/include

Name: foo_dup
Description: foo dup library
Version: 6.6.6

Requires:
Libs: -L${libdir} -L${sharedlibdir} -lfoo
Cflags: -I${includedir} -DFOO
'''

  def __write_example_modules(self):
    tmp_dir = temp_file.make_temp_dir()
    file_util.save(path.join(tmp_dir, 'foo.pc'), self.FOO_PC)
    file_util.save(path.join(tmp_dir, 'bar.pc'), self.BAR_PC)
    file_util.save(path.join(tmp_dir, 'foo_dup.pc'), self.FOO_DUP_PC)
    return tmp_dir

  def test_list_all(self):
    PKG_CONFIG_PATH = [ self.__write_example_modules() ]
    packages = pkg_config.list_all(PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    expected = [
      ( 'bar', 'bar - bar library' ),
      ( 'foo', 'foo - foo library' ),
      ( 'foo_dup', 'foo_dup - foo dup library' ),
    ]
    self.assertEqual( expected, packages )

  def test_cflags_single(self):
    PKG_CONFIG_PATH = [ self.__write_example_modules() ]
    modules = [ 'foo' ]
    cflags = pkg_config.cflags(modules, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    expected = [ '-DFOO', '-I/usr/foo/include' ]
    self.assertEqual( expected, cflags )

  def test_cflags_multiple(self):
    PKG_CONFIG_PATH = [ self.__write_example_modules() ]
    modules = [ 'foo', 'bar' ]
    cflags = pkg_config.cflags(modules, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    expected = [ '-DFOO', '-DBAR', '-I/usr/foo/include', '-I/usr/bar/include' ]
    self.assertEqual( expected, cflags )

  def test_cflags_dups(self):
    PKG_CONFIG_PATH = [ self.__write_example_modules() ]
    modules = [ 'foo', 'foo_dup' ]
    cflags = pkg_config.cflags(modules, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    expected = [ '-DFOO', '-I/usr/foo/include', '-I/usr/foo_dup/include' ]
    self.assertEqual( expected, cflags )

  def test_libs_single(self):
    PKG_CONFIG_PATH = [ self.__write_example_modules() ]
    modules = [ 'foo' ]
    libs = pkg_config.libs(modules, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    expected = [ '-L/usr/foo/lib', '-lfoo' ]
    self.assertEqual( expected, libs )

  def test_libs_multiple(self):
    PKG_CONFIG_PATH = [ self.__write_example_modules() ]
    modules = [ 'foo', 'bar' ]
    libs = pkg_config.libs(modules, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    expected = [ '-L/usr/foo/lib', '-L/usr/bar/lib', '-lfoo', '-lbar' ]
    self.assertEqual( expected, libs )

  def test_libs_dups(self):
    PKG_CONFIG_PATH = [ self.__write_example_modules() ]
    modules = [ 'foo', 'foo_dup' ]
    libs = pkg_config.libs(modules, PKG_CONFIG_PATH = PKG_CONFIG_PATH)
    expected = [ '-L/usr/foo/lib', '-L/usr/foo_dup/lib', '-lfoo' ]
    self.assertEqual( expected, libs )

if __name__ == '__main__':
  unittest.main()
