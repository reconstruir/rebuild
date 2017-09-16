#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, re, subprocess, sys

from bes.fs import compressed_file, file_find, file_util, file_mime, temp_file
from bes.common import algorithm, object_util

class Patch(object):

  @classmethod
  def patch(clazz, patches, cwd, strip = 1, backup = True, posix = True):
    'Apply the given patches by calling patch with strip, backup and posix.'
    patches = object_util.listify(patches)
    target_files = file_find.find(cwd, relative = True)
    for patch in patches:
      rv = clazz.__call_patch(patch, cwd, strip, backup, posix)
      if rv[0] != 0:
        sys.stderr.write(rv[1])
        sys.stderr.flush()
        return rv
    return ( 0, None )

  @classmethod
  def depth(clazz, patch, target_files):
    'Return the depth of a patch relative to target_files.  depth can then be used for Patch.patch(strip = depth)'
    affected_files = clazz.affected_files(patch)
    print("         patch: ", patch)
#    print "affected_files: ", affected_files
#    print "  target_files: ", target_files
    depths = []
    for target in target_files:
      for affected in affected_files:
        d = clazz.__compute_path(affected, target)
        if d != None:
          print("  DEPTH: affected=%s; target=%s;  depth=%d" % (affected, target, d))
          depths.append(d)
    depths = algorithm.unique(depths)
    if len(depths) != 1:
      raise RuntimeError('Unexpected depths for patch: %s' % (patch))
    return depths[0]

  @classmethod
  def __compute_path(clazz, affected, target):
    'Return the depth of a patch relative to target_files.  depth can then be used for Patch.patch(strip = depth)'
    if not affected.endswith(target):
      return None
    if affected == target:
      return 0
    head = file_util.remove_tail(affected, target)
    return head.count(os.sep) + 1
      
  PATCH_FILENAME_EXPRESSION = re.compile(r'^\+\+\+\s+(\S*)\b.*$')

  @classmethod
  def __parse_patch_line(clazz, line):
    f = clazz.PATCH_FILENAME_EXPRESSION.findall(line)
    if not f:
      return None
    if len(f) != 1:
      return None
    return f[0]

  @classmethod
  def affected_files(clazz, patch):
    'Return the list of files the patch will affected.'
    content = clazz.read_patch(patch)
    lines = content.split('\n')
    parsed_lines = [ clazz.__parse_patch_line(line) for line in lines ]
    return [ line for line in parsed_lines if line ]

  @classmethod
  def read_patch(clazz, patch):
    'Return the content of a patch.  Patch can be compressed.'
    if clazz.patch_is_compressed(patch):
      return compressed_file.read(patch)
    return file_util.read(patch)

  @classmethod
  def patch_is_compressed(clazz, patch):
    'Return True if the patch is compressed with gzip.'
    ft = file_mime.mime_type(patch)
    return ft.find('gzip') >= 0

  @classmethod
  def __call_patch(clazz, patch, cwd, strip, backup, posix):

    cmd = [ 'patch', '--force' ]
    
    if strip != None:
      cmd.append('-p%d' % (strip))

    if backup:
      cmd.append('-b')

    if posix:
      cmd.append('--posix')

    # If the patch is compressed, uncompress it to a temp file.
    # Not sure why gzip.open() does not work in this case; i tried.
    if clazz.patch_is_compressed(patch):
      uncompressed_patch = temp_file.make_temp_file(prefix = 'patch_', suffix = '.patch')
      compressed_file.uncompress(patch, uncompressed_patch)
      patch = uncompressed_patch

    with open(patch, 'r') as stdin:
      return clazz.__call_subprocess(cmd, cwd, stdin)
    return ( 1, None )

  @classmethod
  def __call_subprocess(clazz, cmd, cwd, stdin):
    process = subprocess.Popen(cmd,
                               cwd = cwd,
                               stdin = stdin,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.STDOUT)
    out = process.communicate()
    exit_code = process.wait()
    return ( exit_code, out[0] )
