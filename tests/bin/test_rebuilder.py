#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import script_unit_test
from bes.fs import file_replace, tar_util, temp_file
from bes.git import repo
from rebuild.base import build_target
from rebuild.toolchain import toolchain_testing
from bes.testing.unit_test.unit_test_skip import skip_if

from _rebuild_testing.rebuilder_tester import rebuilder_tester

class test_rebuilder_script(script_unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/rebuilder'
  __script__ = __file__, '../../bin/rebuilder.py'
  
  DEBUG = script_unit_test.DEBUG
  #DEBUG = True

  HOST_BUILD_TARGET = build_target.make_host_build_target(level = 'release')
  IOS_BUILD_TARGET = build_target('ios', '', '', ( 'arm64', ), 'release')
  ANDROID_BUILD_TARGET = build_target('android', '', '', ( 'armv7', ), 'release')
  
  DEFAULT_CONFIG = rebuilder_tester.config()
  
  def test_autoconf_with_tarball(self):
    self.maxDiff = None
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'autoconf', 'arsenic')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'arsenic-1.2.9.tar.gz' ], test.artifacts )
  
  def test_autoconf_fructose(self):
    self.maxDiff = None
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'autoconf', 'fructose')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fructose-3.4.5-6.tar.gz' ], test.artifacts )
    self.assertEqual( [
      'files/bin/fructose_print_env',
      'files/bin/fructose_program1',
      'files/bin/fructose_program2',
      'files/bin/rebbe_fructose_print_env',
      'files/bin/rebbe_fructose_program1',
      'files/bin/rebbe_fructose_program2',
      'files/include/fructose1/fructose1.h',
      'files/include/fructose2/fructose2.h',
      'files/lib/libfructose1.a',
      'files/lib/libfructose2.a',
      'files/lib/librebbe_fructose1.a',
      'files/lib/librebbe_fructose2.a',
      'files/lib/pkgconfig/fructose.pc',
      'files/lib/pkgconfig/libfructose1.pc',
      'files/lib/pkgconfig/libfructose2.pc',
      'files/lib/pkgconfig/librebbe_fructose1.pc',
      'files/lib/pkgconfig/librebbe_fructose2.pc',
      'files/lib/pkgconfig/rebbe_fructose.pc',
      'files/lib/rebuild_instructions/fructose.rci',
      'files/lib/rebuild_instructions/libfructose1.rci',
      'files/lib/rebuild_instructions/libfructose2.rci',
      'files/share/doc/fructose/README',
      'metadata/metadata.json',
    ], test.artifacts_members['fructose-3.4.5-6.tar.gz'])

  def test_autoconf_fructose(self):
    self.maxDiff = None
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'autoconf', 'fructose')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fructose-3.4.5-6.tar.gz' ], test.artifacts )
    self.assertEqual( [
      'files/bin/fructose_print_env',
      'files/bin/fructose_program1',
      'files/bin/fructose_program2',
      'files/bin/rebbe_fructose_print_env',
      'files/bin/rebbe_fructose_program1',
      'files/bin/rebbe_fructose_program2',
      'files/include/fructose1/fructose1.h',
      'files/include/fructose2/fructose2.h',
      'files/lib/libfructose1.a',
      'files/lib/libfructose2.a',
      'files/lib/librebbe_fructose1.a',
      'files/lib/librebbe_fructose2.a',
      'files/lib/pkgconfig/fructose.pc',
      'files/lib/pkgconfig/libfructose1.pc',
      'files/lib/pkgconfig/libfructose2.pc',
      'files/lib/pkgconfig/librebbe_fructose1.pc',
      'files/lib/pkgconfig/librebbe_fructose2.pc',
      'files/lib/pkgconfig/rebbe_fructose.pc',
      'files/lib/rebuild_instructions/fructose.rci',
      'files/lib/rebuild_instructions/libfructose1.rci',
      'files/lib/rebuild_instructions/libfructose2.rci',
      'files/share/doc/fructose/README',
      'metadata/metadata.json',
    ], test.artifacts_members['fructose-3.4.5-6.tar.gz'])

  def test_autoconf_fructose_and_fiber(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'autoconf', 'fructose', 'fiber')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fiber-1.0.0.tar.gz', 'fructose-3.4.5-6.tar.gz' ], test.artifacts )

  def xxxtest_autoconf_orange(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'basic', 'orange')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fiber-1.0.0.tar.gz', 'fiber-orange-6.5.4-3.tar.gz', 'fructose-3.4.5-6.tar.gz' ], test.artifacts )

  def test_one_project(self):
    test = self._run_test(rebuilder_tester.config(read_checksums = True), self.data_dir(), 'one_project', 'fructose')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fructose-3.4.5-6.tar.gz' ], test.artifacts )
    self.assertEqual( [ 'fructose-3.4.5-6/sources.checksums', 'fructose-3.4.5-6/targets.checksums' ], test.checksums )
    self.assertEqual( [ 'builds/$SYSTEM-$DISTRO-$DISTRO_VERSION/x86_64/release/fructose-3.4.5-6_timestamp/temp/fructose-3.4.5-6.tar.gz', 'fructose/rebuild.recipe' ],
                      test.checksums_contents['fructose-3.4.5-6/sources.checksums'].filenames() )
    self.assertEqual( [ 'artifacts/$SYSTEM-$DISTRO-$DISTRO_VERSION/x86_64/release/fructose-3.4.5-6.tar.gz' ],
                      test.checksums_contents['fructose-3.4.5-6/targets.checksums'].filenames() )

  def test_tool_tfoo(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'basic', 'tfoo')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'tfoo-1.0.0.tar.gz' ], test.artifacts )
    
  def test_tool_tbar_depends_on_tfoo(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'basic', 'tbar')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'tbar-1.0.0.tar.gz', 'tfoo-1.0.0.tar.gz' ], test.artifacts )

  def test_tool_tbaz(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'basic', 'tbaz')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'tbaz-1.0.0.tar.gz' ], test.artifacts )
    
  def test_lib_libstarch(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'basic', 'libstarch')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libstarch-1.0.0.tar.gz' ], test.artifacts )

  @skip_if(not toolchain_testing.can_compile_ios(), 'cannot compile ios')
  def test_lib_libstarch_ios_cross_compile(self):
    test = self._run_test(rebuilder_tester.config(bt = self.IOS_BUILD_TARGET), self.data_dir(), 'basic', 'libstarch', '-s', 'ios')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libstarch-1.0.0.tar.gz' ], test.artifacts )

  @skip_if(not toolchain_testing.can_compile_android(), 'cannot compile android')
  def test_lib_libstarch_android_cross_compile(self):
    test = self._run_test(rebuilder_tester.config(bt = self.ANDROID_BUILD_TARGET), self.data_dir(), 'basic', 'libstarch', '-s', 'android')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libstarch-1.0.0.tar.gz' ], test.artifacts )

#  def test_lib_libfoo(self):
#    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'basic', 'tfoo')
#    self.assertEqual( 0, test.result.exit_code )
#    self.assertEqual( [ 'libfoo-1.0.0.tar.gz' ], test.artifacts )

#  def test_lib_libbar_depends_on_libfoo(self):
#    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'basic', 'libbar')
#    self.assertEqual( 0, test.result.exit_code )
#    self.assertEqual( [ 'libbar-1.0.0.tar.gz', 'libfoo-1.0.0.tar.gz' ], test.artifacts )
    
  def test_custom_makefile(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'custom_makefile', 'libsomething')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libsomething-1.0.0.tar.gz' ], test.artifacts )

  def test_pc_file_variables(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'pc_file_variables', 'libsomething')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libsomething-1.0.0.tar.gz' ], test.artifacts )

  def test_patch_in_build_dir(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'patch_in_build_dir', 'libfoo')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libfoo-1.0.0.tar.gz' ], test.artifacts )

  def test_patch_in_source_dir(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'patch_in_source_dir', 'fructose')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'fructose-3.4.5-6.tar.gz' ], test.artifacts )

  def test_tarball_git_address(self):
    tmp_dir = self._make_temp_dir()
    project_dir = path.join(self.data_dir(), 'tarball_git_address')
    source_dir = path.join(project_dir, 'src')
    tar_util.copy_tree_with_tar(project_dir, path.join(tmp_dir, 'tarball_git_address'))
    gr = repo.make_temp_repo(delete = not self.DEBUG)
    if self.DEBUG:
      print("temp git repo: ", gr.root)
    tar_util.copy_tree_with_tar(source_dir, gr.root)
    gr.add('.')
    gr.commit('add', '.')
    replacements = {
      '@ADDRESS@': gr.root,
      '@REVISION@': gr.last_commit_hash(short_hash = True),
    }
    recipe_filename = path.join(tmp_dir, 'tarball_git_address', 'libsomething/rebuild.recipe')
    file_replace.replace(recipe_filename, replacements, backup = False)
    test = self._run_test(self.DEFAULT_CONFIG, tmp_dir, 'tarball_git_address', 'libsomething')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libsomething-1.0.0.tar.gz' ], test.artifacts )

  def test_lib_libpotato_depends_on_libstarch(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'basic', 'libpotato')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libpotato-1.0.0.tar.gz', 'libstarch-1.0.0.tar.gz', 'tbar-1.0.0.tar.gz', 'tfoo-1.0.0.tar.gz' ], test.artifacts )
    self.assertTrue( 'files/lib/pkgconfig/libpotato.pc' in test.artifacts_members['libpotato-1.0.0.tar.gz'] )
    
  def test_extra_tarballs(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'extra_tarballs', 'foo', '--source-dir', path.join(self.data_dir(), 'extra_tarballs/source'))
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'foo-1.0.0.tar.gz' ], test.artifacts )
    tgz = path.join(test.artifacts_dir, 'foo-1.0.0.tar.gz')
    self.assertEqual( [
      'files/bin/bar.sh',
      'files/usr/bin/foo.sh',
      'metadata/metadata.json',
    ], test.artifacts_members['foo-1.0.0.tar.gz'])
    
  def test_hooks(self):
    test = self._run_test(rebuilder_tester.config(read_contents = True, read_checksums = True), self.data_dir(), 'hooks', 'foo')
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
    test = self._run_test(rebuilder_tester.config(read_contents = True, read_checksums = True), self.data_dir(), 'env_files', 'fruit')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'carb-1.0.0.tar.gz', 'fiber-1.0.0.tar.gz',  'fruit-1.0.0.tar.gz', 'water-1.0.0.tar.gz' ], test.artifacts )
    self.assertEqual( [
      'env/carb_env.sh',
      'files/bin/carb.py',
      'metadata/metadata.json',
    ], test.artifacts_members['carb-1.0.0.tar.gz'])
    self.assertEqual( [
      'env/water_env.sh',
      'files/bin/water.py',
      'metadata/metadata.json',
    ], test.artifacts_members['water-1.0.0.tar.gz'])
    self.assertEqual( [
      'env/fiber_env.sh',
      'files/bin/fiber.py',
      'metadata/metadata.json',
    ], test.artifacts_members['fiber-1.0.0.tar.gz'])
    self.assertEqual( [
      'env/fruit_env.sh',
      'files/bin/fruit.py',
      'metadata/metadata.json',
    ], test.artifacts_members['fruit-1.0.0.tar.gz'])

    expected = '''#!/usr/bin/env python
print("hook1 hook2")
'''
    
  def test_custom_steps(self):
    test = self._run_test(rebuilder_tester.config(read_contents = True, read_checksums = True), self.data_dir(), 'custom_step', 'foo')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'foo-1.0.0.tar.gz' ], test.artifacts )
    
  def test_run_script(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'run_script', 'foo')
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

  def test_shared_lib_libstarch(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'shared_libs', 'libstarch')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libstarch-1.0.0.tar.gz' ], test.artifacts )

  def xtest_shared_lib_libpotato_depends_on_libstarch(self):
    test = self._run_test(self.DEFAULT_CONFIG, self.data_dir(), 'shared_libs', 'libpotato')
    self.assertEqual( 0, test.result.exit_code )
    self.assertEqual( [ 'libpotato-1.0.0.tar.gz', 'libstarch-1.0.0.tar.gz' ], test.artifacts )
    
  def _run_test(self, config, data_dir, cwd_subdir, *args):
    rt = rebuilder_tester(self._resolve_script(),
                          path.join(data_dir, cwd_subdir),
                          path.normpath(path.join(data_dir, '../sources')),
                          'release',
                          debug = self.DEBUG)
    return rt.run(config, *args)
  
if __name__ == '__main__':
  script_unit_test.main()
