#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
from bes.common import algorithm, dict_util, object_util, string_util
from io import StringIO

class instruction(object):

  def __init__(self, name, flags, requires):
    if not isinstance(name, basestring):
      raise RuntimeError('name should be a string: %s' % (name))
    self.name = name
    if not isinstance(flags, dict):
      raise RuntimeError('flags should be a dict: %s' % (flags))
    if not dict_util.is_homogeneous(flags, basestring, basestring):
      raise RuntimeError('invalid flags.  all keys and values should be strings: %s' % (flags))
    self.flags = flags
    if not isinstance(requires, set):
      raise RuntimeError('requires should be a set: %s' % (requires))
    self.requires = requires

  def __str__(self):
    buf = StringIO()
    buf.write(u'name: ')
    buf.write(unicode(self.name))
    buf.write(u'\n')
    for key in sorted(self.flags.keys()):
      buf.write(unicode(key))
      buf.write(u': ')
      buf.write(unicode(self.flags[key]))
      buf.write(u'\n')
    buf.write(u'requires: ')
    buf.write(unicode(' '.join(self.requires)))
    return buf.getvalue()

  def __eq__(self, other):
    return self.__dict__ == other.__dict__
