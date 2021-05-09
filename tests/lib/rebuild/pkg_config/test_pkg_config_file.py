#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, glob, os.path as path

from bes.testing.unit_test import unit_test
from bes.fs.file_util import file_util

from rebuild.pkg_config.pkg_config_file import pkg_config_file
from rebuild.pkg_config.entry import entry

class test_pkg_config_file(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/pkg_config/real_examples'
  
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
Cflags: -I${includedir}
'''

  FOO_EXPECTED_VARIABLES = [
    entry(entry.VARIABLE, 'prefix', '/usr/foo'),
    entry(entry.VARIABLE, 'exec_prefix', '${prefix}'),
    entry(entry.VARIABLE, 'libdir', '${exec_prefix}/lib'),
    entry(entry.VARIABLE, 'sharedlibdir', '${libdir}'),
    entry(entry.VARIABLE, 'includedir', '${prefix}/include'),
  ]

  FOO_EXPECTED_EXPORTS = [
    entry(entry.EXPORT, 'Name', 'foo'),
    entry(entry.EXPORT, 'Description', 'foo library'),
    entry(entry.EXPORT, 'Version', '1.2.3'),
    entry(entry.EXPORT, 'Requires', ''),
    entry(entry.EXPORT, 'Libs', '-L${libdir} -L${sharedlibdir} -lfoo'),
    entry(entry.EXPORT, 'Cflags', '-I${includedir}'),
  ]

  TEMPLATE_PC = '''prefix=/usr/foo
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
sharedlibdir=${libdir}
includedir=${prefix}/include

Name: @NAME@
Description: @DESCRIPTION@
Version: @VERSION@

Requires:
Libs: -L${libdir} -L${sharedlibdir} -lfoo
Cflags: -I${includedir}
'''

  def test_parse_filename(self):
    filename = self.make_temp_file(content = self.FOO_PC)
    cf = pkg_config_file()
    cf.parse_file(filename)
    self.assertEqual( self.FOO_EXPECTED_VARIABLES, cf.variables )
    self.assertEqual( self.FOO_EXPECTED_EXPORTS, cf.exports )

  def test_parse_string(self):
    cf = pkg_config_file()
    cf.parse_string(self.FOO_PC)
    self.assertEqual( self.FOO_EXPECTED_VARIABLES, cf.variables )
    self.assertEqual( self.FOO_EXPECTED_EXPORTS, cf.exports )

  def test_parse_many_examples(self):
    examples = glob.glob(path.join(self.data_dir(), '*.pc'))
    self.assertTrue( len(examples) > 0 )
    for example in examples:
      cf = pkg_config_file()
      cf.parse_file(example)

####  def test_set_variable(self):
####    cf = pkg_config_file()
####    cf.parse_string(self.FOO_PC)
####    cf.set_variable('prefix', '/something/else')
####    expected_variables = copy.deepcopy(self.FOO_EXPECTED_VARIABLES)
####    self.assertEqual( 'prefix', expected_variables[0].name )
####    expected_variables[0].value = '/something/else'
####    self.assertEqual( expected_variables, cf.variables )
####    self.assertEqual( self.FOO_EXPECTED_EXPORTS, cf.exports )

  def test_deep_copy(self):
    cf = pkg_config_file()
    cf.parse_string(self.FOO_PC)

    copy_cf = cf.deep_copy()
    self.assertEqual( self.FOO_EXPECTED_VARIABLES, cf.variables )
    self.assertEqual( self.FOO_EXPECTED_EXPORTS, cf.exports )

    self.assertEqual( self.FOO_EXPECTED_VARIABLES, copy_cf.variables )
    self.assertEqual( self.FOO_EXPECTED_EXPORTS, copy_cf.exports )

  def test_resolve(self):
    self.maxDiff = None
    
    cf = pkg_config_file()
    cf.parse_string(self.FOO_PC)

    self.assertEqual( self.FOO_EXPECTED_VARIABLES, cf.variables )
    self.assertEqual( self.FOO_EXPECTED_EXPORTS, cf.exports )

    cf.resolve()

    expected_variables = [
      entry(entry.VARIABLE, 'prefix', '/usr/foo'),
      entry(entry.VARIABLE, 'exec_prefix', '/usr/foo'),
      entry(entry.VARIABLE, 'libdir', '/usr/foo/lib'),
      entry(entry.VARIABLE, 'sharedlibdir', '/usr/foo/lib'),
      entry(entry.VARIABLE, 'includedir', '/usr/foo/include'),
    ]
    expected_exports = [
      entry(entry.EXPORT, 'Name', 'foo'),
      entry(entry.EXPORT, 'Description', 'foo library'),
      entry(entry.EXPORT, 'Version', '1.2.3'),
      entry(entry.EXPORT, 'Requires', ''),
      entry(entry.EXPORT, 'Libs', '-L/usr/foo/lib -L/usr/foo/lib -lfoo'),
      entry(entry.EXPORT, 'Cflags', '-I/usr/foo/include'),
    ]
    self.assertEqual( expected_variables, cf.variables )
    self.assertEqual( expected_exports, cf.exports )

####  def test_replace(self):
####    self.maxDiff = None
####    replacements = { 'NAME': 'foobar', 'DESCRIPTION': 'something nice', 'VERSION': '6.6.6' }
####    cf = pkg_config_file()
####    cf.parse_string(self.TEMPLATE_PC)
####    cf.replace(replacements)
####    expected_exports = [
####      entry(entry.EXPORT, 'Name', 'foobar'),
####      entry(entry.EXPORT, 'Description', 'something nice'),
####      entry(entry.EXPORT, 'Version', '6.6.6'),
####      entry(entry.EXPORT, 'Requires', ''),
####      entry(entry.EXPORT, 'Libs', '-L${libdir} -L${sharedlibdir} -lfoo'),
####      entry(entry.EXPORT, 'Cflags', '-I${includedir}'),
####    ]
####    self.assertEqual( expected_exports, cf.exports )

  def test_write_filename(self):
    filename = self.make_temp_file(content = self.FOO_PC)
    cf = pkg_config_file()
    cf.parse_file(filename)
    new_filename = self.make_temp_file()
    cf.write_file(new_filename, backup = False)

    new_cf = pkg_config_file()
    new_cf.parse_file(new_filename)
    
    self.assertEqual( cf, new_cf )

  def test_write_many_examples(self):
    examples = glob.glob(path.join(self.data_dir(), '*.pc'))
    for example in examples:
      cf = pkg_config_file()
      cf.parse_file(example)
      new_filename = self.make_temp_file()
      cf.write_file(new_filename, backup = False)

      new_cf = pkg_config_file()
      new_cf.parse_file(new_filename)
    
      self.assertEqual( cf, new_cf )

  def test_cleanup_duplicate_exports_flags(self):
    self.maxDiff = None
    
    dup_pc = '''prefix=/usr/foo
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
sharedlibdir=${libdir}
includedir=${prefix}/include

Name: foo
Description: foo library
Version: 1.2.3

Requires: foo >= 1.2.3 orange >= 6.6.6 bar baz bar orange >= 6.6.6
Libs: -L${libdir} -L${sharedlibdir} -lfoo -lbar -lfoo -L${libdir} -lfoo
Cflags: -I${includedir} -I${includedir}
'''

    expected_pc = '''prefix=/usr/foo
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
sharedlibdir=${libdir}
includedir=${prefix}/include

Name: foo
Description: foo library
Version: 1.2.3
Requires: foo >= 1.2.3 orange >= 6.6.6 bar baz
Libs: -L${libdir} -L${sharedlibdir} -lfoo -lbar
Cflags: -I${includedir}
'''
    cf = pkg_config_file()
    cf.parse_string(dup_pc)
    cf.cleanup_duplicate_exports()
    self.assertEqual( expected_pc.strip(), str(cf).strip() )

if __name__ == "__main__":
  unit_test.main()
