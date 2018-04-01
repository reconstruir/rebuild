#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy, difflib, os, os.path as path
from bes.compat import StringIO
from bes.fs import dir_util, temp_file
from bes.system import execute, env_var, os_env
from bes.text import text_line_parser
from bes.enum import enum
from collections import namedtuple

class action(enum):
  SET = 1
  UNSET = 2
  PATH_APPEND = 3
  PATH_PREPEND = 4
  PATH_REMOVE = 5

instruction = namedtuple('instruction', 'key,value,action')
  
class env_dir(object):

  def __init__(self, where):
    self._where = path.abspath(where)

  def files(self, relative = True):
    return dir_util.list(self._where, relative = relative)

  def transform_env(self, env):
    new_env = copy.deepcopy(env)
    for inst in self.instructions():
      if inst.action == action.SET:
        new_env[inst.key] = inst.value
      elif inst.action == action.UNSET:
        if inst.key in new_env:
          del new_env[inst.key]
      elif inst.action == action.PATH_APPEND:
        v = env_var(new_env, inst.key)
        v.append(inst.value)
      elif inst.action == action.PATH_PREPEND:
        v = env_var(new_env, inst.key)
        v.prepend(inst.value)
      elif inst.action == action.PATH_REMOVE:
        v = env_var(new_env, inst.key)
        v.remove(inst.value)
    return new_env
    
  def instructions(self):
    files = self.files(relative = False)
    buf = StringIO()
    buf.write('#!/bin/bash\n')
    buf.write('echo "----1----"\n')
    buf.write('env\n')
    buf.write('echo "----2----"\n')
    for f in files:
      buf.write('source \"%s\"\n' % (f))
    buf.write('echo "----3----"\n')
    buf.write('env\n')
    buf.write('echo "----4----"\n')
    script = temp_file.make_temp_file(content = buf.getvalue())
    os.chmod(script, 0o755)
    rv = execute.execute(script, raise_error = True, shell = True)
    parser = text_line_parser(rv.stdout)
    env1 = self._parse_env_lines(parser.cut_lines('----1----', '----2----'))
    env2 = self._parse_env_lines(parser.cut_lines('----3----', '----4----'))
    delta = self._env_delta(env1, env2)
    instructions = []
    for key in delta.added:
      instructions.append(instruction(key, env2[key], action.SET))
      
    for key in delta.removed:
      instructions.append(instruction(key, None, action.UNSET))
      
    for key in delta.changed:
      value1 = env1[key]
      value2 = env2[key]
      for inst in self._determine_change_instructions(key, value1, value2):
        instructions.append(inst)
        
    return instructions
      
  @classmethod
  def _parse_env_lines(clazz, lines):
    result = {}
    for line in lines:
      key, delimiter, value = line.text.partition('=')
      assert delimiter == '='
      result[key] = value
    return result
      
  _delta = namedtuple('_delta', 'added,removed,changed')
  @classmethod
  def _env_delta(clazz, env1, env2):
    'Return delta between env1 and env2.'
    changed = set()
    keys1 = set(env1.keys())
    keys2 = set(env2.keys())
    added = keys2 - keys1
    removed = keys1 - keys2
    common = keys1 & keys2
    for key in common:
      if env1[key] != env2[key]:
        changed.add(key)
    return clazz._delta(added, removed, changed)

  @classmethod
  def _determine_change_instructions(clazz, key, value1, value2):
    if not os_env.key_is_path(key):
      yield instruction(key, value2, action.SET)
      
    p1 = env_var.path_split(value1)
    p2 = env_var.path_split(value2)
    sm = difflib.SequenceMatcher(isjunk = None, a = p1, b = p2)

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
      if tag == 'insert':
        if i1 == 0:
          for p in reversed(p2[j1:j2]):
            yield instruction(key, p, action.PATH_PREPEND)
        else:
          for p in p2[j1:j2]:
            yield instruction(key, p, action.PATH_APPEND)
      elif tag == 'delete':
        for p in p1[i1:i2]:
          yield instruction(key, p, action.PATH_REMOVE)
