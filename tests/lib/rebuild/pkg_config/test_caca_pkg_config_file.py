#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
import copy, glob, os.path as path, unittest
from bes.fs.temp_file import temp_file
from bes.key_value.key_value_list import key_value_list
from rebuild.pkg_config.caca_pkg_config_file import caca_pkg_config_file
#from rebuild.pkg_config.entry import entry

class test_caca_pkg_config_file(unit_test):

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
    ( 'prefix', '/usr/foo' ),
    ( 'exec_prefix', '${prefix}' ),
    ( 'libdir', '${exec_prefix}/lib' ),
    ( 'sharedlibdir', '${libdir}' ),
    ( 'includedir', '${prefix}/include' ),
  ]

  FOO_EXPECTED_PROPERTIES = [
    ( 'Name', 'foo' ),
    ( 'Description', 'foo library' ),
    ( 'Version', '1.2.3' ),
    ( 'Requires', '' ),
    ( 'Libs', '-L${libdir} -L${sharedlibdir} -lfoo' ),
    ( 'Cflags', '-I${includedir}' ),
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

  def test_parse_text(self):
    cf = caca_pkg_config_file.parse_text('<unknown>', self.FOO_PC)
    self.assertEqual( self.FOO_EXPECTED_VARIABLES, cf.variables )
    self.assertEqual( self.FOO_EXPECTED_PROPERTIES, cf.properties )
    
  def test_parse_file(self):
    tmp = temp_file.make_temp_file(content = self.FOO_PC)
    cf = caca_pkg_config_file.parse_file(tmp)
    self.assertEqual( self.FOO_EXPECTED_VARIABLES, cf.variables )
    self.assertEqual( self.FOO_EXPECTED_PROPERTIES, cf.properties )

  def test_parse_many_examples(self):
    examples = glob.glob(path.join(self.data_dir(), '*.pc'))
    self.assertTrue( len(examples) > 0 )
    for example in examples:
      caca_pkg_config_file.parse_file(example)

  def xxxx_set_variable(self):
    cf = caca_pkg_config_file()
    cf.parse_string(self.FOO_PC)
    cf.set_variable('prefix', '/something/else')
    expected_variables = copy.deepcopy(self.FOO_EXPECTED_VARIABLES)
    self.assertEqual( 'prefix', expected_variables[0].name )
    expected_variables[0].value = '/something/else'
    self.assertEqual( expected_variables, cf.variables )
    self.assertEqual( self.FOO_EXPECTED_PROPERTIES, cf.properties )

  def xtest_deep_copy(self):
    cf = caca_pkg_config_file()
    cf.parse_string(self.FOO_PC)

    copy_cf = cf.deep_copy()
    self.assertEqual( self.FOO_EXPECTED_VARIABLES, cf.variables )
    self.assertEqual( self.FOO_EXPECTED_PROPERTIES, cf.properties )

    self.assertEqual( self.FOO_EXPECTED_VARIABLES, copy_cf.variables )
    self.assertEqual( self.FOO_EXPECTED_PROPERTIES, copy_cf.properties )

  def xtest_resolve(self):
    self.maxDiff = None
    
    cf = caca_pkg_config_file()
    cf.parse_string(self.FOO_PC)

    self.assertEqual( self.FOO_EXPECTED_VARIABLES, cf.variables )
    self.assertEqual( self.FOO_EXPECTED_PROPERTIES, cf.properties )

    cf.resolve()

    expected_variables = [
      entry(entry.VARIABLE, 'prefix', '/usr/foo'),
      entry(entry.VARIABLE, 'exec_prefix', '/usr/foo'),
      entry(entry.VARIABLE, 'libdir', '/usr/foo/lib'),
      entry(entry.VARIABLE, 'sharedlibdir', '/usr/foo/lib'),
      entry(entry.VARIABLE, 'includedir', '/usr/foo/include'),
    ]
    expected_properties = [
      entry(entry.EXPORT, 'Name', 'foo'),
      entry(entry.EXPORT, 'Description', 'foo library'),
      entry(entry.EXPORT, 'Version', '1.2.3'),
      entry(entry.EXPORT, 'Requires', ''),
      entry(entry.EXPORT, 'Libs', '-L/usr/foo/lib -L/usr/foo/lib -lfoo'),
      entry(entry.EXPORT, 'Cflags', '-I/usr/foo/include'),
    ]
    self.assertEqual( expected_variables, cf.variables )
    self.assertEqual( expected_properties, cf.properties )

  def xxxx_replace(self):
    self.maxDiff = None
    replacements = { 'NAME': 'foobar', 'DESCRIPTION': 'something nice', 'VERSION': '6.6.6' }
    cf = caca_pkg_config_file()
    cf.parse_string(self.TEMPLATE_PC)
    cf.replace(replacements)
    expected_properties = [
      entry(entry.EXPORT, 'Name', 'foobar'),
      entry(entry.EXPORT, 'Description', 'something nice'),
      entry(entry.EXPORT, 'Version', '6.6.6'),
      entry(entry.EXPORT, 'Requires', ''),
      entry(entry.EXPORT, 'Libs', '-L${libdir} -L${sharedlibdir} -lfoo'),
      entry(entry.EXPORT, 'Cflags', '-I${includedir}'),
    ]
    self.assertEqual( expected_properties, cf.properties )

  def xtest_write_filename(self):
    filename = temp_file.make_temp_file(content = self.FOO_PC)
    cf = caca_pkg_config_file()
    cf.parse_file(filename)

    new_filename = temp_file.make_temp_file()
    cf.write_file(new_filename)

    new_cf = caca_pkg_config_file()
    new_cf.parse_file(new_filename)
    
    self.assertEqual( cf, new_cf )

  def xtest_write_many_examples(self):
    examples = glob.glob(path.join(self.data_path(), '*.pc'))
    for example in examples:
      cf = caca_pkg_config_file()
      cf.parse_file(example)
      new_filename = temp_file.make_temp_file()
      cf.write_file(new_filename)

      new_cf = caca_pkg_config_file()
      new_cf.parse_file(new_filename)
    
      self.assertEqual( cf, new_cf )

  def xtest_cleanup_duplicate_properties_flags(self):
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
    cf = caca_pkg_config_file()
    cf.parse_string(dup_pc)
    cf.cleanup_duplicate_properties()
    self.assertEqual( expected_pc.strip(), str(cf).strip() )

if __name__ == '__main__':
  unittest.main()
