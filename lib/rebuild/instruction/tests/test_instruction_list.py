#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from rebuild.instruction import instruction_list as IL, instruction as I

class test_instruction_list(unit_test):

  __unit_test_data_dir__ = 'test_data/instruction_list'
    
  def test_update(self):
    a = IL()
    a.update(I('foo', { 'x': '5', 'y': 'hi' }, set([ 'bar' ])))
    v = a.values()
    self.assertEqual( 1, len(v) )
    self.assertEqual( I('foo', { 'x': '5', 'y': 'hi' }, set([ 'bar' ])), v[0] )

    a.update(I('bar', { 'x': '10', 'y': 'go' }, set([ 'baz' ])))
    v = a.values()
    self.assertEqual( 2, len(v) )
    self.assertEqual( I('bar', { 'x': '10', 'y': 'go' }, set([ 'baz' ])), v[0] )
    self.assertEqual( I('foo', { 'x': '5', 'y': 'hi' }, set([ 'bar' ])), v[1] )

  def test_add(self):
    a = IL()
    a.update(I('foo', { 'x': '5', 'y': 'hi' }, set([ 'bar' ])))
    b = IL()
    b.update(I('bar', { 'x': '10', 'y': 'go' }, set([ 'baz' ])))
    c = a + b
    it = iter(c.values())
    self.assertEqual( I('bar', { 'x': '10', 'y': 'go' }, set([ 'baz' ])), next(it) )
    self.assertEqual( I('foo', { 'x': '5', 'y': 'hi' }, set([ 'bar' ])), next(it) )
    
  def test_add_invalid(self):
    a = IL()
    a.update(I('foo', { 'x': '5', 'y': 'hi' }, set([ 'bar' ])))
    b = int(6)
    with self.assertRaises(TypeError) as context:
      a + b
    
  def test_parse(self):
    a = IL.parse('name: foo\nx: 5\ny: hi\nrequires: bar\n').values()
    self.assertEqual( 1, len(a) )
    self.assertEqual( I('foo', { 'x': '5', 'y': 'hi' }, set([ 'bar' ])), a[0] )

  def test_load_file(self):
    a = IL.load_file(self.data_path('fruits/fructose.rci')).values()
    it = iter(a)
    self.assertEqual( 3, len(a) )
    self.assertEqual( I('fructose', {}, set([ 'libfructose1', 'libfructose2' ])), next(it) )
    self.assertEqual( I('libfructose1', { 'CFLAGS': '-I${REBUILD_PACKAGE_PREFIX}/include',
                                          'LDFLAGS': '-L${REBUILD_PACKAGE_PREFIX}/lib',
                                          'LIBS': '-lfructose1' }, set()), next(it) )
    self.assertEqual( I('libfructose2', { 'CFLAGS': '-I${REBUILD_PACKAGE_PREFIX}/include -I${REBUILD_PACKAGE_PREFIX}/include/caca',
                                          'LDFLAGS': '-L${REBUILD_PACKAGE_PREFIX}/lib',
                                          'LIBS': '-lfructose2' }, set()), next(it) )

  def test_load_dir(self):
    a = IL.load_dir(self.data_path('fruits')).values()
    self.assertEqual( 9, len(a) )
    it = iter(a)
    self.assertEqual( I('fiber', {}, set([ 'libfiber1', 'libfiber2' ])), next(it) )
    self.assertEqual( I('fructose', {}, set([ 'libfructose1', 'libfructose2' ])), next(it) )
    self.assertEqual( I('libfiber1', { 'CFLAGS': '-I${REBUILD_PACKAGE_PREFIX}/include',
                                       'LDFLAGS': '-L${REBUILD_PACKAGE_PREFIX}/lib',
                                       'LIBS': '-lfiber1' }, set()), next(it) )
    self.assertEqual( I('libfiber2', { 'CFLAGS': '-I${REBUILD_PACKAGE_PREFIX}/include -I${REBUILD_PACKAGE_PREFIX}/include/caca',
                                       'LDFLAGS': '-L${REBUILD_PACKAGE_PREFIX}/lib',
                                       'LIBS': '-lfiber2' }, set()), next(it) )
    self.assertEqual( I('libfructose1', { 'CFLAGS': '-I${REBUILD_PACKAGE_PREFIX}/include',
                                          'LDFLAGS': '-L${REBUILD_PACKAGE_PREFIX}/lib',
                                          'LIBS': '-lfructose1' }, set()), next(it) )
    self.assertEqual( I('libfructose2', { 'CFLAGS': '-I${REBUILD_PACKAGE_PREFIX}/include -I${REBUILD_PACKAGE_PREFIX}/include/caca',
                                          'LDFLAGS': '-L${REBUILD_PACKAGE_PREFIX}/lib',
                                          'LIBS': '-lfructose2' }, set()), next(it) )
    self.assertEqual( I('liborange1', { 'CFLAGS': '-I${REBUILD_PACKAGE_PREFIX}/include',
                                          'LDFLAGS': '-L${REBUILD_PACKAGE_PREFIX}/lib',
                                          'LIBS': '-lorange1' }, set([ 'libfructose1'])), next(it) )
    self.assertEqual( I('liborange2', { 'CFLAGS': '-I${REBUILD_PACKAGE_PREFIX}/include -I${REBUILD_PACKAGE_PREFIX}/include/caca',
                                          'LDFLAGS': '-L${REBUILD_PACKAGE_PREFIX}/lib',
                                          'LIBS': '-lorange2' }, set([ 'libfiber1' ])), next(it) )
    self.assertEqual( I('orange', {}, set([ 'liborange1', 'liborange2' ])), next(it) )

  def test_load_file_with_quoted_content(self):
    a = IL.load_file(self.data_path('quoted.rci')).values()
    self.assertEqual( 1, len(a) )
    self.assertEqual( I('quoted', { 'CFLAGS': '-DNAME="foo bar"'}, set()), a[0] )
    
  def assertEqual(self, expected, actual):
    if type(expected) == I and type(actual) == I:
      expected = str(expected)
      actual = str(actual)
      return super(test_instruction_list, self).assertEqual(expected, actual)

  def test_dependencies(self):
    a = IL.load_dir(self.data_path('fruits'))
    self.assertEqual( ['libfiber1', 'libfructose1', 'liborange1', 'liborange2' ], a.dependencies('orange') )
    
  def test_flags(self):
    a = IL.load_dir(self.data_path('fruits'))
    a.update(IL.load_file(self.data_path('quoted.rci')))
    a.update(IL.load_file(self.data_path('quoted2.rci')))
    actual = a.flags(['liborange2', 'libfiber1', 'quoted', 'quoted2' ])
    expected = {
      'CFLAGS': '-I${REBUILD_PACKAGE_PREFIX}/include -I${REBUILD_PACKAGE_PREFIX}/include/caca -DNAME="foo bar" -DNAME2="bar baz"',
      'LDFLAGS': '-L${REBUILD_PACKAGE_PREFIX}/lib',
      'LIBS': '-lorange2 -lfiber1'
    }
    self.assertEqual( expected, actual )
    
  def test_dependencies_flags(self):
    a = IL.load_dir(self.data_path('fruits'))
    deps = a.dependencies('orange')
    self.assertEqual( ['libfiber1', 'libfructose1', 'liborange1', 'liborange2' ], deps )
    actual = a.flags(deps)
    expected =  {
      'LIBS': '-lfiber1 -lfructose1 -lorange1 -lorange2',
      'CFLAGS': '-I${REBUILD_PACKAGE_PREFIX}/include -I${REBUILD_PACKAGE_PREFIX}/include/caca',
      'LDFLAGS': '-L${REBUILD_PACKAGE_PREFIX}/lib'
    }
    self.assertEqual( expected, actual )
    
if __name__ == "__main__":
  unit_test.main()
