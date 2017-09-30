#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import Shell
from .Sdk import Sdk

class Xcrun(object):

  XCRUN_EXE = 'xcrun'

  @classmethod
  def find_tool(clazz, sdk, tool):
    if not Sdk.is_valid_sdk(sdk):
      raise RuntimeError('Invalid darwin sdk: %s' % (sdk))
    args = [ '--sdk', sdk, '--find', tool ]
    rv = clazz.xcrun(args)
    lines = rv.stdout.strip().split('\n')
    return lines[-1]

  @classmethod
  def xcrun(clazz, args):
    cmd = [ clazz.XCRUN_EXE ] + args
    return Shell.execute(cmd, shell = False)
