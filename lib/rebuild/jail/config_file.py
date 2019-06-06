#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.string_util import string_util
from bes.common.variable import variable

from bes.compat.ConfigParser import ConfigParser

from collections import namedtuple

class config_file(object):

  package = namedtuple('package', 'name,description,include,exclude,missing')
  hooks = namedtuple('hooks', 'pre,post,cleanup')
  jail = namedtuple('jail', 'description,packages,binaries,hooks')
  
  def __init__(self, filename, variables):
    self.filename = filename
    self.jail = self.__load(self.filename, variables)

  @classmethod
  def __load(clazz, filename, variables):
    'Load a jail config and return a jail object.'
    parser = ConfigParser()
    with open(filename, 'r') as fin:
      parser.readfp(fin)
      header = clazz.__load_header(parser, variables)
      packages = [ clazz.__load_package(parser, package_name, variables) for package_name in header.packages ]
      hooks = clazz.__load_hooks(parser, variables)
      return clazz.jail(header.description, packages, header.binaries, hooks)

  @classmethod
  def __load_header(clazz, parser, variables):
    'Load a header sectin from parser.'
    section = parser.items('jail', vars = variables)
    if not section:
      raise RuntimeError('Missing [jail] section: %s' % (filename))
    description = 'none'
    packages = []
    binaries = None
    for item in section:
      key = item[0]
      value = item[1]
      if key == 'description':
        description = value
      elif key == 'packages':
        packages = clazz.__parse_list(value, variables)
      elif key == 'binaries':
        binaries = clazz.__parse_list(value, variables)
    if not packages and not binaries:
      raise RuntimeError('No packages or binaries given: %s' % (filename))
    return clazz.jail(description, packages, binaries, None)

  @classmethod
  def __load_package(clazz, parser, package_name, variables):
    'Load a package section from parser.'
    if not parser.has_section(package_name):
      return clazz.package(package_name, 'none', None, None, None)
    section = parser.items(package_name, vars = variables)
    description = 'none'
    include = None
    exclude = None
    missing = None
    for item in section:
      key = item[0]
      value = item[1]
      if key == 'description':
        description = value
      elif key == 'include':
        include = clazz.__parse_list(value, variables)
      elif key == 'exclude':
        exclude = clazz.__parse_list(value, variables)
      elif key == 'missing':
        missing = clazz.__parse_list(value, variables)
    return clazz.package(package_name, description, include, exclude, missing)

  @classmethod
  def __load_hooks(clazz, parser, variables):
    'Load hooks from parser.'
    if not parser.has_section('hooks'):
      return clazz.hooks(None, None, None)
    section = parser.items('hooks', vars = variables)
    pre = None
    post = None
    cleanup = None
    for item in section:
      key = item[0]
      value = item[1]
      if key == 'pre':
        pre = clazz.__parse_list_lines(value, variables)
      elif key == 'post':
        post = clazz.__parse_list_lines(value, variables)
      elif key == 'cleanup':
        cleanup = clazz.__parse_list_lines(value, variables)
    return clazz.hooks(pre, post, cleanup)

  @classmethod
  def __parse_list(clazz, s, variables):
    result = string_util.split_by_white_space(s, strip = True)
    return [ variable.substitute(x, variables) for x in result ]

  @classmethod
  def __parse_list_lines(clazz, s, variables):
    result = [ x.strip() for x in s.split('\n') ]
    return [ variable.substitute(x, variables) for x in result if x ]
