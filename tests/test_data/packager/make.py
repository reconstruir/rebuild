#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, os, os.path as path
from bes.archive import archiver
from bes.fs import file_replace, file_find, file_util, tar_util
from bes.refactor import files as refactor_files
from rebuild.package.unit_test_packages import unit_test_packages
from rebuild.base import package_descriptor, requirement
from bes.fs import temp_file
from bes.common import variable
from bes.system import os_env, execute

DEBUG = False
#DEBUG = True

DEFAULT_REPLACEMENTS = { 
  '#@REB_01@': '${template}1_REQUIRES="template"',
  '#@REB_02@': 'AC_SUBST(template1_REQUIRES)',
  '#@REB_03@': 'template1_LIBS="-ltemplate1"',
  '#@REB_04@': 'AC_SUBST(template1_LIBS)',
  '#@REB_05@': 'template1_LIBS_PRIVATE=""',
  '#@REB_06@': 'AC_SUBST(template1_LIBS_PRIVATE)', 
  '#@REB_07@': 'template1_CFLAGS="-DTEMPLATE1"',
  '#@REB_08@': 'AC_SUBST(template1_CFLAGS)',
  '#@REB_09@': 'template2_REQUIRES="template"',
  '#@REB_10@': 'AC_SUBST(template2_REQUIRES)',
  '#@REB_11@': 'template2_LIBS="-ltemplate2"',
  '#@REB_12@': 'AC_SUBST(template2_LIBS)',
  '#@REB_13@': 'template2_LIBS_PRIVATE=""',
  '#@REB_14@': 'AC_SUBST(template2_LIBS_PRIVATE)',
  '#@REB_15@': 'template2_CFLAGS="-DTEMPLATE2"',
  '#@REB_16@': 'AC_SUBST(template2_CFLAGS)',
 }
    
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
#      '#@REB_20@': 'PKG_CHECK_MODULES([CACA], [caca])',
      '/*@fruit1_dot_c@*/': 'file:template/code/fruit/fruit1.c',
      '/*@fruit1_dot_h@*/': 'file:template/code/fruit/fruit1.h',
      '/*@fruit2_dot_c@*/': 'file:template/code/fruit/fruit2.c',
      '/*@fruit2_dot_h@*/': 'file:template/code/fruit/fruit2.h',
    } ),
    ( 'pear-1.2.3-1', 'templatedepends', '1.2.3', {
      '/*@pear1_dot_c@*/': 'file:template/code/pear/pear1.c',
      '/*@pear1_dot_h@*/': 'file:template/code/pear/pear1.h',
      '/*@pear2_dot_c@*/': 'file:template/code/pear/pear2.c',
      '/*@pear2_dot_h@*/': 'file:template/code/pear/pear2.h',
    } ),
    ( 'orange-6.5.4-3', 'templatedepends', '1.2.3', {
      '/*@orange1_dot_c@*/': 'file:template/code/orange/orange1.c',
      '/*@orange1_dot_h@*/': 'file:template/code/orange/orange1.h',
      '/*@orange2_dot_c@*/': 'file:template/code/orange/orange2.c',
      '/*@orange2_dot_h@*/': 'file:template/code/orange/orange2.h',
    } ),
    ( 'apple-1.2.3-1', 'templatedepends', '1.2.3', {
      '/*@smoothie1_dot_c@*/': 'file:template/code/smoothie/smoothie1.c',
      '/*@smoothie1_dot_h@*/': 'file:template/code/smoothie/smoothie1.h',
      '/*@smoothie2_dot_c@*/': 'file:template/code/smoothie/smoothie2.c',
      '/*@smoothie2_dot_h@*/': 'file:template/code/smoothie/smoothie2.h',
    } ),
   ]

  xPACKAGES = [
    ( 'pear-1.2.3-1', 'templatedepends', '1.2.3', {
      '/*@pear1_dot_c@*/': 'file:template/code/pear/pear1.c',
      '/*@pear1_dot_h@*/': 'file:template/code/pear/pear1.h',
      '/*@pear2_dot_c@*/': 'file:template/code/pear/pear2.c',
      '/*@pear2_dot_h@*/': 'file:template/code/pear/pear2.h',
    } ),
   ]
  
  for _, _, _, more_replacements in PACKAGES:
    for key, value in more_replacements.items():
      #substitute(clazz, s, d):
      if value.startswith('file:'):
        filename = value.partition(':')[2]
        more_replacements[key] = file_util.read(filename)

  pc_files_dir = path.join(root, '../pkg_config/dependency_tests')
  for package, template_name, template_version, more_replacements in PACKAGES:

    
    template_tarball = path.join(root, '%s-%s.tar.gz' % (template_name, template_version))
    tmp_dir = temp_file.make_temp_dir(delete = not DEBUG)
    if DEBUG:
      print('DEBUG1: tmp_dir=%s' % (tmp_dir))
    print('FUCK: %s' % (package))
    desc = unit_test_packages.TEST_PACKAGES[package]
    print('desc: %s' % (str(desc)))
    pi = desc #desc['package_info']

    version_no_revision = '%s-%s' % (pi.name, pi.version)

    archiver.extract(template_tarball, tmp_dir, base_dir = 'foo', strip_common_ancestor = True)
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

    default_replacements = make_default_replacements(DEFAULT_REPLACEMENTS, pi.name)
    print('FUCK: %s' % (default_replacements))
    replacements = {}
    replacements.update(default_replacements)
    replacements.update({ '[%s]' % (template_version): '[%s]' % (pi.version) })
    replacements.update(more_replacements)
    for k, v in sorted(replacements.items()):
      print('REPLACEMENTS: %s: %s' % (k, v))
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
    env = os_env.make_clean_env(keep_keys = [ 'PATH', 'PKG_CONFIG_PATH' ])
    env['GZIP'] = '-n'
    flat_command = ' && '.join(command)
    execute.execute(flat_command, shell = True, non_blocking = True, env = env)
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
  env = os_env.make_clean_env(keep_keys = [ 'PATH', 'PKG_CONFIG_PATH' ])
  env['GZIP'] = '-n'
  execute.execute(' && '.join(command), shell = True, non_blocking = True, env = env)
  result = path.join(root, '%s-%s.tar.gz' % (template_name, template_version))
  assert path.isfile(result)
  return result

def make_default_replacements(r, name):
  result = {}
  s = {
    'template': name,
    'TEMPLATE': name.upper(),
  }
  for key, value in r.items():
    result[key] = variable.substitute(value, s)
    print('BEFORE: %s' % (value))
    print(' AFTER: %s' % (result[key]))
  return result

if __name__ == '__main__':
  raise SystemExit(main())
  
