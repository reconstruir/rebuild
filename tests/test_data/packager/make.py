#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from bes.archive import archiver
from bes.fs import file_replace, file_find, file_util, tar_util
from bes.refactor import files as refactor_files
from rebuild.package.unit_test_packages import unit_test_packages
from rebuild.base import build_os_env, package_descriptor, requirement
from bes.fs import temp_file
from bes.common import Shell

DEBUG = False
#DEBUG = True

def main():
  root = os.getcwd()
  make_template_tarball(root, 'template', '1.0.0')
  make_template_tarball(root, 'templatedepends', '1.2.3')
  PACKAGES = [
    ( 'fructose-3.4.5-6', 'template', '1.0.0', {} ),
    ( 'mercury-1.2.8-0', 'template', '1.0.0', {} ),
    ( 'arsenic-1.2.9-0', 'template', '1.0.0', {} ),
    ( 'fiber-1.0.0-0', 'template', '1.0.0', {} ),
    ( 'water-1.0.0-0', 'template', '1.0.0', {} ),
    ( 'fruit-1.0.0', 'templatedepends', '1.2.3', {
#      '#@REB_01@': 'PKG_CHECK_MODULES([CACA], [caca])',
      '#@REB_02@': 'fruit1_REQUIRES="fruit"',
      '#@REB_03@': 'AC_SUBST(fruit1_REQUIRES)',
      '#@REB_04@': 'fruit1_LIBS="-lfruit1"',
      '#@REB_05@': 'AC_SUBST(fruit1_LIBS)',
      '#@REB_06@': 'fruit1_LIBS_PRIVATE=""',
      '#@REB_07@': 'AC_SUBST(fruit1_LIBS_PRIVATE)', 
      '#@REB_08@': 'fruit1_CFLAGS="-DFRUIT1"',
      '#@REB_09@': 'AC_SUBST(fruit1_CFLAGS)',
      '#@REB_10@': 'fruit2_REQUIRES="fruit"',
      '#@REB_11@': 'AC_SUBST(fruit2_REQUIRES)',
      '#@REB_12@': 'fruit2_LIBS="-lfruit2"',
      '#@REB_13@': 'AC_SUBST(fruit2_LIBS)',
      '#@REB_14@': 'fruit2_LIBS_PRIVATE=""',
      '#@REB_15@': 'AC_SUBST(fruit2_LIBS_PRIVATE)',
      '#@REB_16@': 'fruit2_CFLAGS="-DDRUIT2"',
      '#@REB_17@': 'AC_SUBST(fruit2_CFLAGS)',
      '/*@fruit1_dot_c@*/': 'file:template/code/fruit/fruit1.c',
      '/*@fruit1_dot_h@*/': 'file:template/code/fruit/fruit1.h',
      '/*@fruit2_dot_c@*/': 'file:template/code/fruit/fruit2.c',
      '/*@fruit2_dot_h@*/': 'file:template/code/fruit/fruit2.h',
    } ),
    ( 'pear-1.2.3-1', 'templatedepends', '1.2.3', {
#      '#@REB_01@': 'PKG_CHECK_MODULES([CACA], [caca])',
      '#@REB_02@': 'pear1_REQUIRES="fruit"',
      '#@REB_03@': 'AC_SUBST(pear1_REQUIRES)',
      '#@REB_04@': 'pear1_LIBS="-lpear1"',
      '#@REB_05@': 'AC_SUBST(pear1_LIBS)',
      '#@REB_06@': 'pear1_LIBS_PRIVATE=""',
      '#@REB_07@': 'AC_SUBST(pear1_LIBS_PRIVATE)',
      '#@REB_08@': 'pear1_CFLAGS="-DPEAR1"',
      '#@REB_09@': 'AC_SUBST(pear1_CFLAGS)',
      '#@REB_10@': 'pear2_REQUIRES="water"',
      '#@REB_11@': 'AC_SUBST(pear2_REQUIRES)',
      '#@REB_12@': 'pear2_LIBS="-lpear2"',
      '#@REB_13@': 'AC_SUBST(pear2_LIBS)',
      '#@REB_14@': 'pear2_LIBS_PRIVATE=""',
      '#@REB_15@': 'AC_SUBST(pear2_LIBS_PRIVATE)',
      '#@REB_16@': 'pear2_CFLAGS="-DPEAR2"',
      '#@REB_17@': 'AC_SUBST(pear2_CFLAGS)',
      '/*@pear1_dot_c@*/': 'file:template/code/pear/pear1.c',
      '/*@pear1_dot_h@*/': 'file:template/code/pear/pear1.h',
      '/*@pear2_dot_c@*/': 'file:template/code/pear/pear2.c',
      '/*@pear2_dot_h@*/': 'file:template/code/pear/pear2.h',
    } ),
    ( 'orange-6.5.4-3', 'templatedepends', '1.2.3', {
      '#@REB_02@': 'orange1_REQUIRES="fruit"',
      '#@REB_03@': 'AC_SUBST(orange1_REQUIRES)',
      '#@REB_04@': 'orange1_LIBS="-lorange1"',
      '#@REB_05@': 'AC_SUBST(orange1_LIBS)',
      '#@REB_06@': 'orange1_LIBS_PRIVATE=""',
      '#@REB_07@': 'AC_SUBST(orange1_LIBS_PRIVATE)',
      '#@REB_08@': 'orange1_CFLAGS="-DORANGE1"',
      '#@REB_09@': 'AC_SUBST(orange1_CFLAGS)',
      '#@REB_10@': 'orange2_REQUIRES="water"',
      '#@REB_11@': 'AC_SUBST(orange2_REQUIRES)',
      '#@REB_12@': 'orange2_LIBS="-lorange2"',
      '#@REB_13@': 'AC_SUBST(orange2_LIBS)',
      '#@REB_14@': 'orange2_LIBS_PRIVATE=""',
      '#@REB_15@': 'AC_SUBST(orange2_LIBS_PRIVATE)',
      '#@REB_16@': 'orange2_CFLAGS="-DORANGE2"',
      '#@REB_17@': 'AC_SUBST(orange2_CFLAGS)',
      '/*@orange1_dot_c@*/': 'file:template/code/orange/orange1.c',
      '/*@orange1_dot_h@*/': 'file:template/code/orange/orange1.h',
      '/*@orange2_dot_c@*/': 'file:template/code/orange/orange2.c',
      '/*@orange2_dot_h@*/': 'file:template/code/orange/orange2.h',
    } ),
    ( 'apple-1.2.3-1', 'templatedepends', '1.2.3', {
      '#@REB_02@': 'apple1_REQUIRES="fruit"',
      '#@REB_03@': 'AC_SUBST(apple1_REQUIRES)',
      '#@REB_04@': 'apple1_LIBS="-lapple1"',
      '#@REB_05@': 'AC_SUBST(apple1_LIBS)',
      '#@REB_06@': 'apple1_LIBS_PRIVATE=""',
      '#@REB_07@': 'AC_SUBST(apple1_LIBS_PRIVATE)',
      '#@REB_08@': 'apple1_CFLAGS="-DAPPLE1"',
      '#@REB_09@': 'AC_SUBST(apple1_CFLAGS)',
      '#@REB_10@': 'apple2_REQUIRES="water"',
      '#@REB_11@': 'AC_SUBST(apple2_REQUIRES)',
      '#@REB_12@': 'apple2_LIBS="-lapple2"',
      '#@REB_13@': 'AC_SUBST(apple2_LIBS)',
      '#@REB_14@': 'apple2_LIBS_PRIVATE=""',
      '#@REB_15@': 'AC_SUBST(apple2_LIBS_PRIVATE)',
      '#@REB_16@': 'apple2_CFLAGS="-DAPPLE2"',
      '#@REB_17@': 'AC_SUBST(apple2_CFLAGS)',
      '/*@apple1_dot_c@*/': 'file:template/code/apple/apple1.c',
      '/*@apple1_dot_h@*/': 'file:template/code/apple/apple1.h',
      '/*@apple2_dot_c@*/': 'file:template/code/apple/apple2.c',
      '/*@apple2_dot_h@*/': 'file:template/code/apple/apple2.h',
    } ),
    ( 'smoothie-1.0.0', 'templatedepends', '1.2.3', {
      '#@REB_02@': 'smoothie1_REQUIRES="orange pear apple"',
      '#@REB_03@': 'AC_SUBST(smoothie1_REQUIRES)',
      '#@REB_04@': 'smoothie1_LIBS="-lsmoothie1"',
      '#@REB_05@': 'AC_SUBST(smoothie1_LIBS)',
      '#@REB_06@': 'smoothie1_LIBS_PRIVATE=""',
      '#@REB_07@': 'AC_SUBST(smoothie1_LIBS_PRIVATE)',
      '#@REB_08@': 'smoothie1_CFLAGS="-DSMOOTHIE1"',
      '#@REB_09@': 'AC_SUBST(smoothie1_CFLAGS)',
      '#@REB_10@': 'smoothie2_REQUIRES="water"',
      '#@REB_11@': 'AC_SUBST(smoothie2_REQUIRES)',
      '#@REB_12@': 'smoothie2_LIBS="-lsmoothie2"',
      '#@REB_13@': 'AC_SUBST(smoothie2_LIBS)',
      '#@REB_14@': 'smoothie2_LIBS_PRIVATE=""',
      '#@REB_15@': 'AC_SUBST(smoothie2_LIBS_PRIVATE)',
      '#@REB_16@': 'smoothie2_CFLAGS="-DSMOOTHIE2"',
      '#@REB_17@': 'AC_SUBST(smoothie2_CFLAGS)',
      '/*@smoothie1_dot_c@*/': 'file:template/code/smoothie/smoothie1.c',
      '/*@smoothie1_dot_h@*/': 'file:template/code/smoothie/smoothie1.h',
      '/*@smoothie2_dot_c@*/': 'file:template/code/smoothie/smoothie2.c',
      '/*@smoothie2_dot_h@*/': 'file:template/code/smoothie/smoothie2.h',
    } ),
   ]

  for _, _, _, more_replacements in PACKAGES:
    for key, value in more_replacements.items():
      if value.startswith('file:'):
        filename = value.partition(':')[2]
        more_replacements[key] = file_util.read(filename)

  pc_files_dir = path.join(root, '../pkg_config/dependency_tests')
  for package, template_name, template_version, more_replacements in PACKAGES:
    template_tarball = path.join(root, '%s-%s.tar.gz' % (template_name, template_version))
    tmp_dir = temp_file.make_temp_dir(delete = not DEBUG)
    if DEBUG:
      print('DEBUG1: tmp_dir=%s' % (tmp_dir))
    desc = unit_test_packages.TEST_PACKAGES[package]
    pi = desc['package_info']

    version_no_revision = '%s-%s' % (pi.name, pi.version.upstream_version)

    archiver.extract(template_tarball, tmp_dir, base_dir = 'foo', strip_common_base = True)
    working_dir = path.join(tmp_dir, 'foo')
    if DEBUG:
      print('working_dir=%s' % (working_dir))
    refactor_files.refactor(template_name, pi.name, [ working_dir ])

    file_paths = [
      path.join(working_dir, 'configure.ac'),
      path.join(working_dir, 'libs/%s1/%s1.c' % (pi.name, pi.name)),
      path.join(working_dir, 'libs/%s1/%s1.h' % (pi.name, pi.name)),
      path.join(working_dir, 'libs/%s2/%s2.c' % (pi.name, pi.name)),
      path.join(working_dir, 'libs/%s2/%s2.h' % (pi.name, pi.name)),
    ]
    
    replacements = { '[%s]' % (template_version): '[%s]' % (pi.version.upstream_version) }
    replacements.update(more_replacements)
    for f in file_paths:
      file_replace.replace(f, replacements, backup = False)

    command = [
      'cd %s' % (working_dir),
      'automake -a',
      'autoconf',
      './configure',
      'make dist',
      'cp %s.tar.gz %s' % (version_no_revision, root),
    ]
    env = build_os_env.make_clean_env(keep_keys = [ 'PATH', 'PKG_CONFIG_PATH' ])
    env['GZIP'] = '-n'
    flat_command = ' && '.join(command)
    Shell.execute(flat_command, shell = True, non_blocking = True, env = env)
    pc_files = file_find.find_fnmatch(working_dir, [ '*.pc' ], relative = False)
    for pc_file in pc_files:
      dst_pc_file = path.join(pc_files_dir, path.basename(pc_file))
      file_util.copy(pc_file, dst_pc_file)
    
def make_template_tarball(root, template_name, template_version):
  tmp_dir = temp_file.make_temp_dir(delete = not DEBUG)
  if DEBUG:
    print('DEBUG2: tmp_dir=%s' % (tmp_dir))
  full_name = '%s-%s' % (template_name, template_version)
  template_dir = path.join(root, 'template')
  tar_util.copy_tree_with_tar(template_dir, tmp_dir)
  working_dir = path.join(tmp_dir, full_name)
  tarball_filename = '%s.tar.gz' % (full_name)
  command = [
    'cd %s' % (working_dir),
    'automake -a',
    'autoconf',
    './configure',
    'make dist',
    'cp %s %s' % (tarball_filename, root),
    ]
  env = build_os_env.make_clean_env(keep_keys = [ 'PATH', 'PKG_CONFIG_PATH' ])
  env['GZIP'] = '-n'
  Shell.execute(' && '.join(command), shell = True, non_blocking = True, env = env)
  result = path.join(root, '%s-%s.tar.gz' % (template_name, template_version))
  assert path.isfile(result)
  return result
  
if __name__ == '__main__':
  raise SystemExit(main())
  
