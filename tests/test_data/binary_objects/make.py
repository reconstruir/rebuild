#!/usr/bin/env python

from bes.system import host
from bes.common import string_util
from bes.fs import file_util
import os.path as path

DEBUG = False
#DEBUG = True

if host.is_macos():
  COMPILER = 'clang++'
  CFLAGS = [ '--std=c++11' ]
else:
  COMPILER = 'g++'
  CFLAGS = []

ALL_LIBRARY_ARCHS = [ 'i386', 'x86_64', 'armv7', 'arm64' ]
FAT_ARCHS = ALL_LIBRARY_ARCHS
THIN_ARCHS = [ 'x86_64' ]
EXE_ARCHS = [ 'i386', 'x86_64' ]
ARCHS_64 = [ 'x86_64', 'arm64' ]
ARCHS_32 = [ 'i386', 'armv7' ]

FRUIT_SOURCES = [ 'cherry.cpp', 'kiwi.cpp' ]
EXE_SOURCES = FRUIT_SOURCES + [ 'main.cpp' ]
  
def main():

  _make_lib(COMPILER, 'fruits.a', FRUIT_SOURCES, 'fat_all', FAT_ARCHS, False)
  _make_lib(COMPILER, 'fruits.a', FRUIT_SOURCES, 'fat_64', ARCHS_64, False)
  _make_lib(COMPILER, 'fruits.a', FRUIT_SOURCES, 'fat_32', ARCHS_32, False)

  _make_lib(COMPILER, 'fruits.so', FRUIT_SOURCES, 'fat_all', FAT_ARCHS, True)
  _make_lib(COMPILER, 'fruits.so', FRUIT_SOURCES, 'fat_64', ARCHS_64, True)
  _make_lib(COMPILER, 'fruits.so', FRUIT_SOURCES, 'fat_32', ARCHS_32, True)

  for arch in ALL_LIBRARY_ARCHS:
    _make_lib(COMPILER, 'fruits_%s.a' % (arch), FRUIT_SOURCES, 'thin', [ arch ], False)
    _make_lib(COMPILER, 'fruits_%s.so' % (arch), FRUIT_SOURCES, 'thin', [ arch ], True)

  # FAT .o
  _make_object(COMPILER, 'avocado.cpp', 'fat', FAT_ARCHS)

  # THIN .o
  for arch in ALL_LIBRARY_ARCHS:
    _make_object(COMPILER, 'avocado.cpp', 'thin_%s' % (arch), [ arch ])

  _make_junk('notalib.txt', 'this is not a lib\n')
  _make_junk('empty.txt', '')
  _make_junk('size1.txt', '1')
  _make_junk('size2.txt', '12')
  _make_junk('size3.txt', '123')
  _make_junk('size4.txt', '1234')
  _make_junk('size5.txt', '12345')
  _make_junk('size6.txt', '123456')
  _make_junk('size7.txt', '1234567')
  _make_junk('size8.txt', '12345678')
  _make_junk('size9.txt', '123456789')
  _make_junk('size10.txt', '1234567890')

  _make_exe(COMPILER, 'program.exe', EXE_SOURCES, 'fat', EXE_ARCHS)

  for arch in EXE_ARCHS:
    _make_exe(COMPILER, 'program_%s.exe' % (arch), EXE_SOURCES, 'thin', [ arch ])

  for arch in ALL_LIBRARY_ARCHS:
    static_library = 'lib%s.a' % (arch)
    _make_lib(COMPILER, static_library, FRUIT_SOURCES, None, [ arch ], False)

    shared_library = 'lib%s.so' % (arch)
    _make_lib(COMPILER, shared_library, FRUIT_SOURCES, None, [ arch ], True)

  return 0

def _object_from_source(source, object_extension, label):
  name = file_util.remove_extension(source)
  if label:
    return '${SYSTEM}/%s_%s.%s' % (label, name, object_extension)
  else:
    return '${SYSTEM}/%s.%s' % (name, object_extension)

def _make_junk(name, content):
  obj = _resolve_filename(_object_from_source(name, 'txt', None))
  file_util.save(obj, content = content, mode = 0644)

def _make_lib(compiler, library, sources, label, archs, shared):
  objects = [ _object_from_source(s, 'o', label) for s in sources ]
  arch_flags = _make_arch_flags(archs)
  if label:
    library = '${SYSTEM}/%s_%s' % (label, library)
  else:
    library = '${SYSTEM}/%s' % (library)
  for obj, src in zip(objects, sources):
    _compile(compiler, obj, src, arch_flags)
  if shared:
    _make_shared_lib(library, objects)
  else:
    _make_static_lib(library, objects)

def _make_object(compiler, source, label, archs):
  obj = _object_from_source(source, 'o', label)
  arch_flags = _make_arch_flags(archs)
  if DEBUG:
    print("       obj: ", obj)
    print("arch_flags: ", arch_flags)
    print("    source: ", source)
  _compile(compiler, obj, source, arch_flags)

def _compile(compiler, target, source, cflags):
  target = _resolve_filename(target)
  file_util.mkdir(path.dirname(target))
  cmd = [ compiler ] + CFLAGS + cflags + [ '-c', '-o', target, source ] 
  _shell_cmd(cmd)

def _make_macos_lib(target, objects, shared):
  target = _resolve_filename(target)
  objects = _resolve_filenames(objects)
  file_util.mkdir(path.dirname(target))
  if shared:
    shared_flag = '-dynamic'
  else:
    shared_flag = '-static'
    
  cmd = [ 'libtool', shared_flag, '-o', target ] + objects
  _shell_cmd(cmd)

def _make_linux_static_lib(target, objects):
  target = _resolve_filename(target)
  objects = _resolve_filenames(objects)
  file_util.mkdir(path.dirname(target))
  cmd = [ 'ar', 'r', target ] + objects
  _shell_cmd(cmd)

def _make_static_lib(target, objects):
  if host.is_macos():
    _make_macos_lib(target, objects, False)
  else:
    _make_linux_static_lib(target, objects)

def _make_arch_flags(archs):
  'Return compiler flags for the given list of archs.'
  if host.is_linux():
    return []
  arch_flags = []
  for arch in archs:
    arch_flags += [ '-arch', arch ]
  return arch_flags

def _make_linux_shared_lib(target, objects):
  target = _resolve_filename(target)
  objects = _resolve_filenames(objects)
  file_util.mkdir(path.dirname(target))
  cmd = [ COMPILER, '-shared', '-o', target ] + objects
  _shell_cmd(cmd)

def _make_shared_lib(target, objects):
  if host.is_macos():
    _make_macos_lib(target, objects, True)
  else:
    _make_linux_shared_lib(target, objects)

def _link_exe(target, objects, arch_flags):
  target = _resolve_filename(target)
  objects = _resolve_filenames(objects)
  file_util.mkdir(path.dirname(target))
  cmd = [ COMPILER, '-o', target ] + arch_flags + objects
  _shell_cmd(cmd)

def _make_exe(compiler, exe, sources, label, archs):
  objects = [ _object_from_source(s, 'o', label) for s in sources ]
  arch_flags = _make_arch_flags(archs)
  if label:
    exe = '${SYSTEM}/%s_%s' % (label, exe)
  else:
    exe = '${SYSTEM}/%s' % (exe)
  for obj, src in zip(objects, sources):
    _compile(compiler, obj, src, arch_flags)
  _link_exe(exe, objects, arch_flags)

def _resolve_filename(filename):
  filename = filename.replace('${SYSTEM}', host.SYSTEM)
  return filename

def _resolve_filenames(filenames):
  return [ _resolve_filename(f) for f in filenames ]

def _shell_cmd(cmd):
  if DEBUG:
    print("CMD: %s" % (' '.join(cmd)))
  rv = execute.execute(cmd, stderr_to_stdout = True, raise_error = False)
  if rv.exit_code != 0:
    print(rv.stdout)
    raise SystemExit(rv.exit_code)
  
if __name__ == '__main__':
  raise SystemExit(main())
