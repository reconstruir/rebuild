#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import getpass, os.path as path, subprocess

from bes.common.json_util import json_util

from .sudo_exe import sudo_exe

class sudo(object):
  'Class to deal with sudo.'

  _INFO_FILE_PATH = path.expanduser('~/bes/sudo/info.json')
  _VERSION = '1'
  
  @classmethod
  def ensure_can_call_program(clazz, user, program, info_file_path = None):
    'Ensure that sudo can be used for program by user without a password.'
    if not path.isabs(program):
      raise RuntimeError('path is not an absolute path: %s' % (program))
    info = clazz._info_load(clazz._INFO_FILE_PATH)
    key = '%s_%s' % (user, program)
    print("info: ", info)
    if key in info:
      return True
    return False

  @classmethod
  def _info_load(clazz, filename):
    'Load info.'
    try:
      return json_util.read_file(filename) or {}
    except IOError, ex:
      return {}

  @classmethod
  def _info_save(clazz, filename, info):
    'Save info.'
    return json_util.save_file(filename, info, indent = 2)

  @classmethod
  def _make_sudo_line(clazz, user, program, version):
    'Make one line of sudo config.'
    return '%s ALL = (root) NOPASSWD: %s # bes_sudo:v%d' % (user, program, clazz._VERSION)

  @classmethod
  def call_sudo(clazz, args, cwd = None, msg = None, prompt = 'sudo password: '):
    'Call sudo.'
    return sudo_exe.call_sudo(args, cwd = cwd, msg = msg, prompt = prompt)
