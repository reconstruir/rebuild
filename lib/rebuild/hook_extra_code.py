#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

HOOK_EXTRA_CODE = '''\
from rebuild.step_manager import Step, step_aborted, step_result, step_register, step_registry
from rebuild.packager.steps import *
from rebuild.packager import Check, check_result
from rebuild.packager.checks import *
'''
