#!/usr/bin/env python
#-*- coding:utf-8 -*-

import getpass, os.path as path, subprocess
from bes.common import json_util
from bes.system import execute

#from mac_address import mac_address
#import re

class sudo(object):
  'Lookup mac address by alias.'

  __INFO_FILE_PATH = path.expanduser('~/bes/sudo/info.json')
  __VERSION = '1'
  
  @classmethod
  def ensure_can_call_program(clazz, user, program, info_file_path = None):
    'Ensure that sudo can be used for program by user without a password.'
    if not path.isabs(program):
      raise RuntimeError('path is not an absolute path: %s' % (program))
    info = clazz.__info_load(clazz.__INFO_FILE_PATH)
    key = '%s_%s' % (user, program)
    print("info: ", info)
    if key in info:
      return True
    print("CACA:")
    return False

  @classmethod
  def __info_load(clazz, filename):
    'Load info.'
    try:
      return json_util.read_file(filename) or {}
    except IOError, ex:
      return {}

  @classmethod
  def __info_save(clazz, filename, info):
    'Save info.'
    return json_util.save_file(filename, info, indent = 2)

  @classmethod
  def __make_sudo_line(clazz, user, program, version):
    'Make one line of sudo config.'
    return '%s ALL = (root) NOPASSWD: %s # bes_sudo:v%d' % (user, program, clazz.__VERSION)

  @classmethod
  def sudo_subprocess(clazz, cmd, prompt = 'sudo password: '):
    'Make one line of sudo config.'

    cmd = execute.listify_command(cmd)

    if '-S' in cmd:
      password = getpass.getpass(prompt = prompt)
      input_data = password + '\n'
    else:
      input_data = None
      
    process = subprocess.Popen(cmd,
                               stdout = subprocess.PIPE,
                               stdin = subprocess.PIPE,
                               stderr = subprocess.PIPE,
                               universal_newlines = True)
    output = process.communicate(input_data)
    stdout_data = output[0]
    stderr_data = output[1]
    exit_code = process.wait()

    return execute.Result(stdout_data, stderr_data, exit_code)
