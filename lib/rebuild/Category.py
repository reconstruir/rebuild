#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class Category(object):

  LIB = 'lib'
  TOOL = 'tool'

  CATEGORIES = [ LIB, TOOL ]

  @classmethod
  def category_is_valid(clazz, s):
    return s in clazz.CATEGORIES
