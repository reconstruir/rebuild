#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, os.path as path, re
from bes.system import impl_import
from bes.fs.dir_util import dir_util
from bes.fs.file_util import file_util
from bes.fs.file_path import file_path

from bes.system import host
if host.SYSTEM == 'macos':
  from .library_macos import library_macos as _library_super_class
elif host.SYSTEM == 'linux':
  from .library_linux import library_linux as _library_super_class

#_library_super_class = impl_import.load(__name__, 'library', globals())

class library(_library_super_class):
  'Top level class for dealing with system libraries.'

  @classmethod
  def is_static_library(clazz, filename):
    'Return True if filename is a shared library.'
    if not path.isfile(filename) or path.islink(filename):
      return False
    if clazz.is_archive(filename):
      return True
    return super(library, clazz).is_static_library(filename)

  @classmethod
  def is_archive(clazz, filename):
    'Return True if filename is an ar archive'
    if not path.isfile(filename) or path.islink(filename):
      return False
    with open(filename, 'rb') as fin:
      magic = fin.read(8)
      return len(magic) == 8 and magic == b'!<arch>\n'

  @classmethod
  def is_library(clazz, filename):
    'Return True if filename is any kind of static or shared library.'
    if not path.isfile(filename) or path.islink(filename):
      return False
    return clazz.is_static_library(filename) or clazz.is_shared_library(filename)

  @classmethod
  def dependencies_recursive(clazz, filename):
    'Return all the dependencies for a binary recursively.'
    result = set()
    return sorted(list(clazz._deps_recurse(filename, result)))
        
  @classmethod
  def _deps_recurse(clazz, filename, result):
    'Get deps and recurse into them to find more deps.'
    deps = clazz.dependencies(filename) or []
    to_check = set()
    for dep in deps:
      if dep not in result:
        to_check.add(dep)
        result.add(dep)
    for dep in to_check:
      result.add(dep)
      clazz._deps_recurse(dep, result)
    return result

  @classmethod
  def list_libraries(clazz, d, relative = True):
    'List all libraries in a directory.  Does not rescurse into subdirs.  Resulting paths are absolute.'
    files = dir_util.list(d, relative = False)
    libs = [ f for f in files if clazz.is_library(f) ]
    if relative:
      libs = [ file_util.remove_head(f, d) for f in libs ]
    return libs
    
  _NAME_PATTERNS = [
    re.compile(r'.*lib([^\..]*)\.*.*\.dylib'),
    re.compile(r'.*lib(.*)\.so.*'),
    re.compile(r'lib(.*)\.a'),
  ]

  @classmethod
  def name(clazz, filename):
    'Return the just the name of the library stripping prefix, extension and version.'
    for pattern in clazz._NAME_PATTERNS:
      v = pattern.findall(path.basename(filename))
      if len(v) == 1:
        return v[0]
    return None

  @classmethod
  def name_add_prefix(clazz, filename, prefix):
    'Add a prefix to the name of a libary filename.  libfoo.a => libprefix_foo.a'
    name = clazz.name(filename)
    if not name:
      return None
    return filename.replace(name, prefix + name)
  
  @classmethod
  def relative_rpath(clazz, filename, library):
    'Return relative rpath'
    prefix = path.commonprefix([filename, library])
    if prefix == os.sep:
      return None
    filename_depth = file_path.depth(filename)
    library_depth = file_path.depth(library)
    prefix_depth = file_path.depth(prefix)
    filename_rel = file_util.remove_head(filename, prefix)
    library_rel = file_util.remove_head(library, prefix)
    if filename_depth == library_depth == prefix_depth:
      return ''
    delta_depth = filename_depth - prefix_depth
    library_dir = path.dirname(library_rel)
#    print('    filename: %s (%d)' % (filename, filename_depth))
#    print('     library: %s (%d)' % (library, library_depth))
#    print('      prefix: %s (%d)' % (prefix, prefix_depth))
#    print('filename_rel: %s' % (filename_rel))
#    print(' library_rel: %s' % (library_rel))
#    print(' delta_depth: %s' % (delta_depth))
#    print(' library_dir: %s' % (library_dir))

    between = os.sep.join(['..'] * (delta_depth - 1))
    result = path.join(between, library_rel)
#    print('      result: %s' % (result))
    
    return result
