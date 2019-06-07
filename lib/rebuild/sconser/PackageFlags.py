#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# TODO: add duplicate flag handling

from bes.common.object_util import object_util

class PackageFlags(object):

  VARIABLES = [ 'cpppath', 'libpath', 'shlinkflags', 'libs' ]

  def __init__(self, cpppath = None, libpath = None, shlinkflags = None, libs = None):
    cpppath = cpppath or []
    libpath = libpath or []
    shlinkflags = shlinkflags or []
    libs = libs or []

    self.cpppath = cpppath
    self.libpath = libpath
    self.shlinkflags = shlinkflags
    self.libs = libs

  def __str__(self):
    values = [ getattr(self, var) for var in self.VARIABLES ]
    value_strings = [ '%s=%s' % (var, value) for var, value in zip(self.VARIABLES, values) ]
    return '; '.join(value_strings)

  @property
  def cpppath(self):
    return self._cpppath

  @cpppath.setter
  def cpppath(self, cpppath):
    self._cpppath = object_util.listify(cpppath)

  @property
  def libpath(self):
    return self._libpath

  @libpath.setter
  def libpath(self, libpath):
    self._libpath = object_util.listify(libpath)

  @property
  def shlinkflags(self):
    return self._shlinkflags

  @shlinkflags.setter
  def shlinkflags(self, shlinkflags):
    self._shlinkflags = object_util.listify(shlinkflags)

  @property
  def libs(self):
    return self._libs

  @libs.setter
  def libs(self, libs):
    self._libs = object_util.listify(libs)

  def __add__(self, other):
    self.cpppath += other.cpppath
    self.libpath += other.libpath
    self.shlinkflags += other.shlinkflags
    self.libs += other.libs
    return self

  @classmethod
  def sum(clazz, flags):
    'Sum up a list of flags.  flags can also be a single object.'
    result = PackageFlags()
    for next_flags in object_util.listify(flags):
      result += next_flags
    return result

  def to_scons_environment(self):
    'Return a dictionary of variables that can be used in the scons environment.'
    d = {}
    for var in self.VARIABLES:
      d[var.upper()] = getattr(self, var)
    return d
