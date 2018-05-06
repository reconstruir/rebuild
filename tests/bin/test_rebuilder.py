#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import script_unit_test
from bes.fs import file_find, temp_file
from bes.archive import archiver
from bes.system import host
from collections import namedtuple
from rebuild.base import build_arch, build_level, build_system, build_target

class test_rebuilder_script(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/rebuilder'
  __script__ = __file__, '../../bin/rebuilder.py'

  DEBUG = script_unit_test.DEBUG
  #DEBUG = True

  BUILD_LEVEL = 'release'

  BUILD_TARGET = build_target(system = build_system.HOST,
                              level = build_level.RELEASE,
                              archs = build_arch.DEFAULT_HOST_ARCHS)
  
  _test_context = namedtuple('_test_context', 'tmp_dir,command,result,artifacts_dir,artifacts,artifacts_members,artifacts_contents,droppings')

  def test_basic_fructose(self):
    test = self._run_test(False, 'basic', 'fructose')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fructose-3.4.5-6.tar.gz' ], test.artifacts )

  def test_one_project(self):
    test = self._run_test(False, 'one_project', 'fructose')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fructose-3.4.5-6.tar.gz' ], test.artifacts )
    
  def test_fructose_and_fiber(self):
    test = self._run_test(False, 'basic', 'fructose', 'fiber')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fiber-1.0.0.tar.gz', 'fructose-3.4.5-6.tar.gz' ], test.artifacts )
    
  def xxxtest_orange(self):
    test = self._run_test(False, 'basic', 'fructose', 'fiber')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fiber-1.0.0.tar.gz', 'fiber-orange-6.5.4-3.tar.gz', 'fructose-3.4.5-6.tar.gz' ], test.artifacts )

  def test_tool_tfoo(self):
    test = self._run_test(False, 'basic', 'tfoo')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'tfoo-1.0.0.tar.gz' ], test.artifacts )
    
  def test_tool_tbar_depends_on_tfoo(self):
    test = self._run_test(False, 'basic', 'tbar')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'tbar-1.0.0.tar.gz', 'tfoo-1.0.0.tar.gz' ], test.artifacts )

  def test_tool_tbaz(self):
    test = self._run_test(False, 'basic', 'tbaz')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'tbaz-1.0.0.tar.gz' ], test.artifacts )
    
  def test_lib_libstarch(self):
    test = self._run_test(False, 'basic', 'libstarch')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libstarch-1.0.0.tar.gz' ], test.artifacts )

  def test_lib_libpotato_depends_on_libstarch(self):
    test = self._run_test(False, 'basic', 'libpotato')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libpotato-1.0.0.tar.gz', 'libstarch-1.0.0.tar.gz', 'tbar-1.0.0.tar.gz', 'tfoo-1.0.0.tar.gz' ], test.artifacts )
    self.assertTrue( 'files/lib/pkgconfig/libpotato.pc' in test.artifacts_members['libpotato-1.0.0.tar.gz'] )
    
  def test_extra_tarballs(self):
    test = self._run_test(False, 'extra_tarballs', 'foo', '--source-dir', path.join(self.data_dir(), 'extra_tarballs/source'))
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'foo-1.0.0.tar.gz' ], test.artifacts )
    tgz = path.join(test.artifacts_dir, 'foo-1.0.0.tar.gz')
    self.assertEqual( [
      'files/bin/bar.sh',
      'files/usr/bin/foo.sh',
      'metadata/metadata.json',
    ], test.artifacts_members['foo-1.0.0.tar.gz'])
    
  def test_hooks(self):
    test = self._run_test(True, 'hooks', 'foo')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'foo-1.0.0.tar.gz' ], test.artifacts )
    tgz = path.join(test.artifacts_dir, 'foo-1.0.0.tar.gz')
    self.assertEqual( [
      'files/bin/foo.py',
      'metadata/metadata.json',
    ], test.artifacts_members['foo-1.0.0.tar.gz'])
    expected = '''#!/usr/bin/env python
print("hook1 hook2")
'''
    self.assertMultiLineEqual( expected, test.artifacts_contents['foo-1.0.0.tar.gz']['files/bin/foo.py'] )
    
  def test_env_files(self):
    test = self._run_test(True, 'env_files', 'foo')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'foo-1.0.0.tar.gz' ], test.artifacts )
    tgz = path.join(test.artifacts_dir, 'foo-1.0.0.tar.gz')
    self.assertEqual( [
      'env/foo_env1.sh',
      'env/foo_env2.sh',
      'files/bin/foo.py',
      'metadata/metadata.json',
    ], test.artifacts_members['foo-1.0.0.tar.gz'])

    expected = '''#!/usr/bin/env python
print("hook1 hook2")
'''

  def test_run_script(self):
    test = self._run_test(False, 'run_script', 'foo')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'foo-1.0.0.tar.gz' ], test.artifacts )
    self.assertEqual( [
      'files/bin/foo1.sh',
      'files/bin/foo2.sh',
      'metadata/metadata.json',
    ], test.artifacts_members['foo-1.0.0.tar.gz'])

  def _make_temp_dir(self):
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    if self.DEBUG:
      print("tmp_dir: ", tmp_dir)
    return tmp_dir

  def _make_command(self, tmp_dir, *args):
    cmd = [
      '--source-dir',
      path.join(self.data_dir(), '../packager'),
      '--no-network',
      '-v',
      '--root', tmp_dir,
      '--level', self.BUILD_LEVEL,
      '--timestamp', 'timestamp',
    ] + list(args)
    return cmd

  def _run_test(self, read_contents, cwd_subdir, *args):
    tmp_dir = self._make_temp_dir()
    command = self._make_command(tmp_dir, *args)
    cwd = path.join(self.data_dir(), cwd_subdir)
    artifacts_dir = path.join(tmp_dir, 'artifacts', self.BUILD_TARGET.build_path)
    result = self.run_script(command, cwd = cwd)
    artifacts = file_find.find(artifacts_dir)
    droppings = file_find.find(tmp_dir)
    artifacts_members = {}
    artifacts_contents = {}
    if result.exit_code == 0:
      for artifact in artifacts:
        artifact_path = path.join(artifacts_dir, artifact)
        artifacts_members[artifact] = archiver.members(artifact_path)
        if read_contents:
          artifacts_contents[artifact] = self._artifact_contents(artifact_path)
      
    if result.exit_code != 0 or self.DEBUG:
      self.spew(result.stdout)
      
    return self._test_context(tmp_dir, command, result, artifacts_dir, artifacts, artifacts_members, artifacts_contents, droppings)

  @classmethod
  def _blacklist(clazz, member, patterns):
    for pattern in patterns:
      if pattern in member:
        return True
    return False
  
  @classmethod
  def _artifact_contents(clazz, artifact):
    result = {}
    for member in archiver.members(artifact):
      if not clazz._blacklist(member, [ 'bin/rebbe_', 'lib/librebbe_' ]):
        result[member] = archiver.extract_member_to_string(artifact, member).decode('utf8')
    return result
  
if __name__ == '__main__':
  script_unit_test.main()
