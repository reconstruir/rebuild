#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

class recipe(namedtuple('recipe', 'filename,properties,requirements,build_requirements,descriptor,instructions,steps')):

  def __new__(clazz, filename, properties, requirements, build_requirements,
              descriptor, instructions, steps):
    return clazz.__bases__[0].__new__(clazz, filename, properties, requirements,
                                      build_requirements, descriptor, instructions, steps)
