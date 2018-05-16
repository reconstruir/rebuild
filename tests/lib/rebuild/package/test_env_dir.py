#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-
import copy, os, os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_util, temp_file
from bes.fs.testing import temp_content
from rebuild.package.env_dir import env_dir, action

class test_env_dir(unit_test):

  _save_environ = None
    
  @classmethod
  def setUpClass(clazz):
    clazz._save_environ = copy.deepcopy(os.environ)

  @classmethod
  def tearDownClass(clazz):
    assert os.environ == clazz._save_environ
    
  def test_files(self):
    ed = self._make_temp_env_dir([
      'file 1.sh "export A=1\n" 644',
      'file 2.sh "export B=2\n" 644',
      'file 3.sh "export C=3\n" 644',
      'file 4.sh "export D=4\n" 644',
      'file 5.sh "export E=5\n" 644',
      'file 6.sh "unset F\n" 644',
    ])
    self.assertEqual( [ '1.sh', '2.sh', '3.sh', '4.sh', '5.sh', '6.sh' ], ed.files() )
  
  def test_instructions_set(self):
    ed = self._make_temp_env_dir([
      'file 1.sh "export FOO=1\n" 644',
    ])
    env = {}
    self.assertEqual( [
      ( 'FOO', '1', action.SET ),
    ], ed.instructions({}) )
  
  def test_instructions_path_prepend(self):
    ed = self._make_temp_env_dir([
      'file 1.sh "export PATH=/foo/bin:$PATH\n" 644',
    ])
    env = {
      'PATH': '/usr/bin:/bin',
    }
    self.assertEqual( [
      ( 'PATH', '/foo/bin', action.PATH_PREPEND ),
    ], ed.instructions(env) )
  
  def test_instructions_path_append(self):
    ed = self._make_temp_env_dir([
      'file 1.sh "export PATH=$PATH:/foo/bin\n" 644',
    ])
    env = {
      'PATH': '/usr/bin:/bin',
    }
    self.assertEqual( [
      ( 'PATH', '/foo/bin', action.PATH_APPEND ),
    ], ed.instructions(env) )
  
  def test_instructions_path_remove(self):
    ed = self._make_temp_env_dir([
      'file 1.sh "export PATH=/usr/bin:/bin\n" 644',
    ])
    env = {
      'PATH': '/usr/bin:/my/path:/bin',
    }
    self.assertEqual( [
      ( 'PATH', '/my/path', action.PATH_REMOVE ),
    ], ed.instructions(env) )
  
  def xtest_foo(self):
    save_env = copy.deepcopy(os.environ)
    
    os.environ['SOMETHINGIMADEUP'] = 'GOOD'

    save_path = os.environ['PATH']
    test_path = '/bin:/usr/bin:/my/path:/sbin'
    os.environ['PATH'] = test_path

    try:
      tmp_dir = temp_content.write_items_to_temp_dir([
        'file 1.sh "export PATH=/bin:/usr/bin:/sbin\n" 644',
        'file 2.sh "export BAR=orange\n" 644',
        'file 3.sh "export PATH=/a/bin:$PATH\nexport PATH=/b/bin:$PATH\n" 644',
        'file 4.sh "export FOO=kiwi\n" 644',
        'file 5.sh "export PATH=$PATH:/x/bin\nPATH=$PATH:/y/bin\n" 644',
        'file 6.sh "unset SOMETHINGIMADEUP\n" 644',
      ])
#      tmp_dir = temp_file.make_temp_dir()
#      file_util.save(path.join(tmp_dir, '1.sh'), content = 'export PATH=/bin:/usr/bin:/sbin\n')
#      file_util.save(path.join(tmp_dir, '2.sh'), content = 'export BAR=orange\n')
#      file_util.save(path.join(tmp_dir, '3.sh'), content = 'export PATH=/a/bin:$PATH\nexport PATH=/b/bin:$PATH\n')
#      file_util.save(path.join(tmp_dir, '4.sh'), content = 'export FOO=kiwi\n')
#      file_util.save(path.join(tmp_dir, '5.sh'), content = 'export PATH=$PATH:/x/bin\nPATH=$PATH:/y/bin\n')
#      file_util.save(path.join(tmp_dir, '6.sh'), content = 'unset SOMETHINGIMADEUP\n')
      ed = env_dir(tmp_dir)
      self.assertEqual( [ '1.sh', '2.sh', '3.sh', '4.sh', '5.sh', '6.sh' ], ed.files() )
      self.assertEqual( [
        ( 'BAR', 'orange', action.SET ),
        ( 'FOO', 'kiwi', action.SET ),
        ( 'PATH', '/a/bin', action.PATH_PREPEND ),
        ( 'PATH', '/b/bin', action.PATH_PREPEND ),
        ( 'PATH', '/my/path', action.PATH_REMOVE ),
        ( 'PATH', '/x/bin', action.PATH_APPEND ),
        ( 'PATH', '/y/bin', action.PATH_APPEND ),
        ( 'SOMETHINGIMADEUP', None, action.UNSET ),
      ], ed.instructions() )

      self.assertEqual( {
        'BAR': 'orange',
        'FOO': 'kiwi',
        'PATH': '/b/bin:/a/bin:/x/bin:/y/bin',
      }, ed.transform_env({}) )
        
      self.assertEqual( {
        'BAR': 'orange',
        'FOO': 'kiwi',
        'PATH': '/b/bin:/a/bin:/x/bin:/y/bin',
      }, ed.transform_env({ 'SOMETHINGIMADEUP': 'yes' }) )
        
      self.assertEqual( {
        'BAR': 'orange',
        'FOO': 'kiwi',
        'PATH': '/b/bin:/a/bin:/usr/local/bin:/usr/foo/bin:/x/bin:/y/bin',
      }, ed.transform_env({ 'PATH': '/usr/local/bin:/usr/foo/bin' }) )
        
    finally:
#      assert save_env == os.environ
      os.environ['PATH'] = save_path

  def _make_temp_env_dir(self, items):
    tmp_dir = temp_content.write_items_to_temp_dir(items)
    return env_dir(tmp_dir)
      
if __name__ == '__main__':
  unit_test.main()
