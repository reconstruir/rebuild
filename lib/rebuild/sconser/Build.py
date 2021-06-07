#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from datetime import datetime
import os, os.path as path, platform, sys

from bes.common.object_util import object_util
from bes.common.tuple_util import tuple_util
from bes.system.execute import execute
from bes.system.console import console
from bes.text import text_canvas

from bes.build.build_blurb import build_blurb
from bes.build.build_target import build_target
from .PackageFlags import PackageFlags

class Build(object):

  SPEW_LOW = 0
  SPEW_MED = 1
  SPEW_HI = 2

  PackageFlags = PackageFlags

  blurb = build_blurb.blurb

  def __init__(self, scons_locals, verbose = SPEW_MED):
    self._scons_locals = tuple_util.dict_to_named_tuple('SconsLocals', scons_locals)

    self.verbose = verbose

    self.env = SConsEnvironment() #PRINT_CMD_LINE_FUNC = self.print_cmd_line)
    scons_vars = self._scons_locals.variables()

    scons_vars.Add(self._scons_locals.Enumvariable(
      'system',
      'The system to build for',
      build_target.HOST_SYSTEM_NAME,
      allowed_values = set(build_target.SYSTEMS)))

    scons_vars.Add(self._scons_locals.Enumvariable(
      'build_level',
      'The build type',
      build_target.DEBUG,
      allowed_values = set(build_target.LEVELS)))

    PRINT_CMD_LINE_FUNC = self.print_cmd_line
    #PRINT_CMD_LINE_FUNC = None
    self.env = self._scons_locals.Environment(variables = scons_vars,
                              PRINT_CMD_LINE_FUNC = PRINT_CMD_LINE_FUNC)

    unknown_vars = scons_vars.Unknownvariables()
    if unknown_vars:
      raise RuntimeError('Unknown scons variables: "%s"' % (unknown_vars))

    self.env['BES_BUILD'] = self

    self.build_target = build_target()

    self.source_dir = os.getcwd()
    self.target_dir = path.abspath(path.join(self.build_target.build_path, 'BUILD'))
    self.obj_dir = path.join(self.target_dir, 'obj')
    self.bin_dir = path.join(self.target_dir, 'bin')
    self.unit_test_dir = path.join(self.target_dir, 'unit_tests')
    self.lib_dir = path.join(self.target_dir, 'lib')
    self.include_dir = path.join(self.target_dir, 'include')

    self._longest_target = 0

    self._packages = {}

    self._pkg_config_exe = path.join(self.__get_package_home_dir('pkg-config'), 'bin/pkg-config')

    self.add_package('__builtin__', PackageFlags(cpppath = self.include_dir, libpath = self.lib_dir))

    # FIXME: conditionalize this on verbosity level
#    self.env.AppendUnique(CCCOMSTR = 'compile c')
#    self.env.AppendUnique(CXXCOMSTR = 'compile c++')
#    self.env.AppendUnique(LINKCOMSTR = 'link')
#    self.env.AppendUnique(ARCOMSTR = 'archive')
#    self.env.AppendUnique(RANLIBCOMSTR = 'ranlib')

#    self.env.AppendUnique(CCFLAGS = [ '-std=c++11' ])

    self.register_builder('_unit_test_runner_builder', self._unit_test_runner_builder)

  def register_builder(self, name, action):
    builder = self.env.Builder(action = action)
    self.env.AppendUnique(BUILDERS = { name : builder })

  def package_flags(self, packages):
    flags = PackageFlags()
    for package in object_util.listify(packages):
      flags += self._packages[package]
    return flags

#    self.env.AppendUnique(CPPPATH = cpppath)
#    self.env.AppendUnique(LIBPATH = libpath)
#    self.env.AppendUnique(SHLINKFLAGS = shlinkflags)
#    self.env.AppendUnique(LIBS = libs)

  def include_path_add(self, path_or_paths):
    path_or_paths = object_util.listify(path_or_paths)
    self.env.AppendUnique(CPPPATH = path_or_paths)

  def __run_pkg_config(self, pkg_config_path, packages):
    assert pkg_config_path
    assert path.isdir(pkg_config_path)
    # Use a tmp environment because ParseConfig sets cflags as a side effect and
    # we don't always want to do that.  We want to set flags only when a builder
    # has explicit dependencies on a specific package.
    tmp_env = self._scons_locals.Environment()
    cmd = 'PKG_CONFIG_PATH=%s %s %s --cflags --libs' % (pkg_config_path, self._pkg_config_exe, ' '.join(packages))
    tmp_env.ParseConfig(cmd)
    return PackageFlags(cpppath = tmp_env['CPPPATH'],
                        libpath = tmp_env['LIBPATH'],
                        shlinkflags = tmp_env['SHLINKFLAGS'],
                        libs = tmp_env['LIBS'])

  def add_pkg_config_package(self, package_name):
    self.add_package(package_name, self.__get_pkg_config_flags(package_name))

  def add_package(self, package_name, package_flags):
    assert not self._packages.has_key(package_name)
    self._packages[package_name] = package_flags

  def add_static_package(self, package_name, libs):
    package_home_dir = self.__get_package_home_dir(package_name)
    lib_dir = path.join(package_home_dir, 'lib')
    include_dir = path.join(package_home_dir, 'include')
    flags = PackageFlags(cpppath = include_dir, libpath = lib_dir, libs = libs)
    self.add_package(package_name, flags)

  def __get_pkg_config_flags(self, package_name):
    pkg_config_path = self.__get_pkg_config_dir(package_name)
    return self.__run_pkg_config(pkg_config_path, [ package_name ])

  def __get_package_home_dir(self, package_name):
    p = '~/projects/site/%s/%s' % (platform.system(), package_name)
    return path.expanduser(p)

  def __get_pkg_config_dir(self, package_name):
    return path.join(self.__get_package_home_dir(package_name), 'lib/pkgconfig')

  def __get_scons_builder_flags(self, flags, packages):
    builtin_flags = self._packages['__builtin__']
    packages_flags = PackageFlags.sum([ self._packages[package_name] for package_name in packages ])
    flags_flags = PackageFlags.sum(flags)

    builder_flags = PackageFlags()
    builder_flags += builtin_flags
    builder_flags += packages_flags
    builder_flags += flags_flags

    #print "      program: %s" % (target)
    #print "     packages: %s" % (packages)
    #print "builder_flags: %s" % (builder_flags)
    #print

    return builder_flags

  def unit_test(self, target, source, flags = PackageFlags(), packages = [], verbose = False, *args, **kwargs):
    builder_flags = self.__get_scons_builder_flags(flags, packages)
    scons_args = builder_flags.to_scons_environment()
    scons_args.update(kwargs)

#    print "TARGET: ", target
#    for k, v in sorted(scons_args.items()):
#      print "  %s: %s" % (k, v)
#    print ""

    builder = self.env.Program(target = target,
                               source = source,
                               __BES_LABEL = 'build unit test',
                               *args, **scons_args)
    self.__report_new_targets(builder)
    installer = self.install_unit_test(builder)

    stamp_path = installer[0].get_abspath() + '.unit.passed'

    #if verbose:
    #  scons_args.update({ 'PRINT_CMD_LINE_FUNC': None })


    runner = self.env._unit_test_runner_builder(stamp_path, installer, __BES_LABEL = 'unit test run', __BES_VERBOSE = verbose)
    self.__report_new_targets(runner)
    self.env.Depends(self.make_dir_node('.'), runner)

    return runner
  
  @staticmethod
  def _unit_test_runner_builder(target, source, env):
    self = env['BES_BUILD']
    verbose = env['__BES_VERBOSE']

    binary_path = source[0].get_abspath()
    stamp_path = target[0].get_abspath()

    runner_env = {
      '_BES_BUILD_CWD': os.getcwd(),
      '_BES_BUILD_SOURCE_DIR': self.source_dir,
    }

    non_blocking = verbose

    rv = execute.execute(binary_path, raise_error = False,
                         non_blocking = non_blocking,
                         stderr_to_stdout = True,
                         env = runner_env)

    if rv.exit_code != 0:
      sys.stdout.write(rv.stdout)

    stamp_content = str(datetime.now()) + '\n'

    open(stamp_path, 'w').write(stamp_content)

    return rv.exit_code

  def __report_new_targets(self, targets):
    targets = object_util.listify(targets)
    longest_new_target = max(len(str(target)) for target in targets)
    self._longest_target = max(self._longest_target, longest_new_target)
    
  def program(self, target, source,
              flags = PackageFlags(), packages = [],
              *args, **kwargs):
    builder_flags = self.__get_scons_builder_flags(flags, packages)
    scons_args = builder_flags.to_scons_environment()
    scons_args.update(kwargs)
    builder = self.env.Program(target = target,
                               source = source,
                               __BES_LABEL = 'build program',
                               *args, **scons_args)
    self.__report_new_targets(builder)
    return self.install_bin(builder)

  def static_library(self, target, source,
                     flags = PackageFlags(), packages = [],
                     headers = None, header_prefix = None,
                     *args, **kwargs):

    headers = headers or []
    header_prefix = header_prefix or ''

    for header in headers:
      self.install_header(path.join(self.include_dir, header_prefix), header)

    builder_flags = self.__get_scons_builder_flags(flags, packages)
    scons_args = builder_flags.to_scons_environment()
    scons_args.update(kwargs)

    builder = self.env.StaticLibrary(target = target,
                                     source = source,
                                     *args, **scons_args)
    self.__report_new_targets(builder)
    installer = self.install_lib(builder)
    self.env.Depends(self.make_dir_node('.'), installer)

    self.add_package(target, PackageFlags(libs = target))

    return installer

  def process_subdirs(self, subdirs, top_level = False, *args, **kargs):

    result = []
    for subdir in subdirs:
      sconscript = path.join(path.join(subdir, 'SConscript'))

      if top_level:
        subdir_kargs = {}
        subdir_kargs.update(kargs)
        subdir_kargs['variant_dir'] = self.make_dir_node(path.join(self.obj_dir, subdir))
        subdir_kargs['duplicate'] = 0
      else:
        subdir_kargs = kargs
        
      rv = self.env.SConscript([ sconscript ], *args, **subdir_kargs)
      result.append(rv)
    return result
  
  def make_dir_node(self, d):
    return self.env.fs.Dir(d)

  def make_file_node(self, d):
    return self.env.fs.File(d)

  def install_bin(self, node):
    assert node != None
    installer = self.env.Install(self.bin_dir, node, __BES_LABEL = 'install bin')
    self.__report_new_targets(installer)
    return installer

  def install_unit_test(self, node):
    assert node != None
    installer = self.env.Install(self.unit_test_dir, node, __BES_LABEL = 'install unit test')
    self.__report_new_targets(installer)
    return installer

  def install_lib(self, node):
    assert node != None
    installer = self.env.Install(self.lib_dir, node, __BES_LABEL = 'install lib')
    self.__report_new_targets(installer)
    return installer

  def install_header(self, include_dir, node):
    assert node != None
    installer = self.env.Install(include_dir, node, __BES_LABEL = 'install header')
    self.__report_new_targets(installer)
    return installer

  @staticmethod
  def print_cmd_line(s, target, source, env):
    self = env['BES_BUILD']
    
    try:
      label = env['__BES_LABEL']
    except:
      label = s

    # FIXME: unify this with build_blurb.blurb()
    label = '%s:' % (label)

    justified_label = build_blurb.justified_label(label)

    width = console.terminal_width(default = 80)

    target_strings = [ str(n) for n in target ]
    source_strings = [ str(n) for n in source ]

    target_len = len(target_strings)
    source_len = len(source_strings)

    longest_target_string = max([ len(n) for n in target_strings ])
    longest_source_string = max([ len(n) for n in source_strings ])

    assert longest_target_string <= self._longest_target

    #longest_target_string = self._longest_target

    target_label = str(target)

    stuff = [ str(n) for n in target ]
    target_label = stuff
    
    canvas = text_canvas(terminal.width(), max(source_len, target_len) + 1)

    x = 0
    y = 0
    canvas.draw_text(x, y, justified_label)

    x += len(justified_label) + 1

    canvas.draw_text_lines(x, y, target_strings)

    x += longest_target_string + 1

    canvas.draw_text_lines(x, y, source_strings)

    if self.verbose == self.SPEW_LOW:
      pass
    elif  self.verbose == self.SPEW_MED:
      pass
    elif  self.verbose == self.SPEW_HI:
      pass

    print(str(canvas).rstrip())
