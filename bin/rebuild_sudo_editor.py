#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

# A script to edit sudoers.  FIXME: needs major audit for security issues

# For chicken-n-egg issues this program uses only python standard libs.

import os, os.path as path, argparse, shutil, tempfile

DEFAULT_SUDOERS = '/etc/sudoers'

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument('--sudoers', '-s', action = 'store', default = DEFAULT_SUDOERS,
                  help = 'sudoers files to user [ %s ]' % (DEFAULT_SUDOERS))
  ap.add_argument('username', action = 'store', type = str, help = 'username')
  ap.add_argument('program', action = 'store', type = str, help = 'program')
  ap.add_argument('version', action = 'store', type = str, help = 'version')

  args = ap.parse_args()

  if not path.isfile(args.sudoers):
    raise RuntimeError('No such sudoers file: %s' % (args.sudoers))
  
  print(" sudoers: ", args.sudoers)
  print("username: ", args.username)
  print(" program: ", args.program)
  print(" version: ", args.version)

  content = __read_file(args.sudoers)
  line = __make_sudo_line(args.username, args.program, args.version)

  # Check if the line is already in sudoers
  if content.find(line) >= 0:
    return 0

  new_content = content + line + '\n'
  __backup(args.sudoers)
  __save_atomic(args.sudoers, new_content, mode = os.stat(args.sudoers).st_mode)
  return 0

def __read_file(filename):
  with open(filename, 'r') as fin:
    return fin.read()
  
def __make_sudo_line(username, program, version):
  'Make one line of sudo config.'
  return '%s ALL = (root) NOPASSWD: %s # bes_sudo:v%s' % (username, program, version)

def __save_atomic(filename, content, mode = None):
  'Atomically save content to filename using an intermediate temporary file.'
  dirname, basename = os.path.split(filename)
  #clazz.mkdir(path.dirname(filename))
  tmp = tempfile.NamedTemporaryFile(prefix = basename, dir = dirname, delete = False, mode = 'w')
  if content:
    tmp.write(content)
  tmp.flush()
  os.fsync(tmp.fileno())
  tmp.close()
  if mode:
    os.chmod(tmp.name, mode)
  os.rename(tmp.name, filename)

def __backup(filename, suffix = '.bak'):
  'Make a backup of filename if it exists.'
  if path.exists(filename):
    if path.isfile(filename):
      backup_filename = filename + suffix
      if path.exists(backup_filename):
        os.remove(backup_filename)
      shutil.copy(filename, backup_filename)
      os.chmod(backup_filename, os.stat(filename).st_mode)
    else:
      raise RuntimeError('Not a file: %s' % (filename))

def run():
  raise SystemExit(main())

if __name__ == '__main__':
  raise SystemExit(main())
