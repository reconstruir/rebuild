#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common import Shell
from .darwin_sdk import darwin_sdk

class xcrun(object):

  XCRUN_EXE = 'xcrun'

  @classmethod
  def xcrun(clazz, args):
    cmd = [ clazz.XCRUN_EXE ] + args
    return Shell.execute(cmd, shell = False)

  @classmethod
  def find_tool(clazz, sdk, tool):
    if not darwin_sdk.is_valid_sdk(sdk):
      raise RuntimeError('Invalid macos sdk: %s' % (sdk))
    args = [ '--sdk', sdk, '--find', tool ]
    rv = clazz.xcrun(args)
    lines = rv.stdout.strip().split('\n')
    return lines[-1]

  @classmethod
  def sdk_path(clazz, sdk):
    if not darwin_sdk.is_valid_sdk(sdk):
      raise RuntimeError('Invalid macos sdk: %s' % (sdk))
    args = [ '--sdk', sdk, '--show-sdk-path' ]
    rv = clazz.xcrun(args)
    return rv.stdout.strip()
