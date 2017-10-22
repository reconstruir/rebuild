#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class checksum_manager(object):
  'Manage checksums.'

  def __init__(self, checksum_dir):
    self._checksum_dir = checksum_dir
    print('FUCK: checksum_dir: %s' % (self._checksum_dir))
    self._ignored = set()
    self._ignore_all = False

  @property
  def ignore_all(self):
    return self._ignore_all
    
  @ignore_all.setter
  def ignore_all(self, ignore_all):
    self._ignore_all = ignore_all

  def ignore(self, name):
    self._ignored.add(name)

  def is_ignored(self, name):
    return self._ignore_all or name in self._ignored
