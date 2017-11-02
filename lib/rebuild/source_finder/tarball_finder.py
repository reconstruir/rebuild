#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path, re
from bes.common import algorithm, object_util, string_util
from bes.fs import file_find

class tarball_finder(object):

  @classmethod
  def find(clazz, dirs, name, version):
    dirs = object_util.listify(dirs)
    filenames = []
    for d in dirs:
      if path.isdir(d):
        filenames += file_find.find(d, max_depth = 4, relative = False, file_type = file_find.FILE | file_find.LINK)
    return clazz.find_in_list(filenames, name, version)

  @classmethod
  def find_in_list(clazz, filenames, name, version):
    'Find the filenames that match name and version.'

    name_replacements = {
      'lib': '',
    }
    name_prefix = clazz._name_prefix(name)
    #print('cACA: name=%s;  name_prefix=%s' % (name, name_prefix))
    if name_prefix:
      name_replacements[name_prefix] = ''
    name = re.escape(string_util.replace(name, name_replacements, word_boundary = False))
    version = re.escape(version)
    version = version.replace('\\.', '.')
    version = version.replace('\\-', '.')

    patterns = [
      r'.*%s.*%s.*' % (name, version),
      r'.*%s.*%s.*' % (name.replace('-', '_'), version),
      r'.*%s.*%s.*' % (name.replace('_', '-'), version),
      r'.*%s.*%s.*' % (name.replace('.', '_'), version),
      r'.*%s.*%s.*' % (name.replace('_', '.'), version),
    ]
    expressions = []
    for pattern in patterns:
      expressions.append(re.compile(pattern))
      expressions.append(re.compile(pattern, re.IGNORECASE))

    result = []
    for filename in filenames:
      for i, expression in enumerate(expressions):
        base = path.basename(filename)
        #print('CHECKING %s to %s => %s' % (expression.pattern, base, expression.match(base)))
        if expression.match(base):
          result.append(filename)
    return sorted(algorithm.unique(result))

  @classmethod
  def _name_prefix(clazz, name):
    'Return the name prefix if it exists.  foo_xyz => foo;  xyz => None.'
    i = name.find('_')
    if i < 0:
      return None
    return name[0 : i + 1]
