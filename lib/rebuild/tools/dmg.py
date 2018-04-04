#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path
from bes.compat.plistlib import plistlib_loads

from bes.fs import file_check, file_find, file_util, tar_util, temp_file
from bes.system import execute, log

from collections import namedtuple

log.configure('dmg=info format=brief')

class dmg(object):
  'Class to deal with dmg files on macos.'

  mount_info = namedtuple('mount_info', 'filename, mount_point, entries')

  @classmethod
  def info(clazz):
    rv = clazz._execute_cmd('hdiutil', 'info', '-plist')
    return plistlib_loads(rv.stdout).get('images', [])

  @classmethod
  def contents(clazz, dmg):
    file_check.check_file(dmg)
    mnt = clazz._mount_at_temp_dir(dmg)
    files = file_find.find(mnt.mount_point, relative = True, file_type = file_find.FILE_OR_LINK)
    clazz._eject(mnt.mount_point)
    return files

  @classmethod
  def extract(clazz, dmg, dst_dir):
    file_check.check_file(dmg)
    file_util.mkdir(dst_dir)
    mnt = clazz._mount_at_temp_dir(dmg)
    tar_util.copy_tree_with_tar(mnt.mount_point, dst_dir)
    clazz._eject(mnt.mount_point)

  @classmethod
  def _mount_at_temp_dir(clazz, dmg):
    file_check.check_file(dmg)
    tmp_dir = temp_file.make_temp_dir()
    rv = clazz._execute_cmd('hdiutil', 'attach', '-mountpoint', tmp_dir, '-plist', dmg)
    entries = plistlib_loads(rv.stdout)
    return clazz.mount_info(dmg, tmp_dir, entries.get('system-entities', []))

  @classmethod
  def _eject(clazz, mount_point):
    clazz._execute_cmd('hdiutil', 'eject', mount_point)
  
  @classmethod
  def _execute_cmd(clazz, *args):
    cmd = ' '.join(args)
    clazz.log_i('executing: "%s"' % (cmd))
    return execute.execute(cmd)

log.add_logging(dmg, 'dmg')
