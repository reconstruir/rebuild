#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# FIXME: unify the replacements here with those in step_pkg_config_make_pc.py

import copy
from rebuild.step_manager import Step, step_result

def _save_args(args):
  assert isinstance(args, dict)
  return copy.deepcopy(args)

class sample_step_save_args1(Step):
  def __init__(self):
    self.tag = 'sample_step_save_args1'
    super(sample_step_save_args1, self).__init__()
    self.saved_args = None

  def execute(self, argument):
    self.log_d('%s: execute(argument=%s)' % (self, argument))
    self.saved_args = _save_args(argument.args)
    return step_result(True, None)

  def on_tag_changed(self):
    pass
  
  @classmethod
  def parse_step_args(clazz, packager_env, args):
    keys = [ key for key in args.keys() if key.startswith('desc1_') ]
    return { key: args[key] for key in keys }

class sample_step_save_args2(Step):
  def __init__(self):
    super(sample_step_save_args2, self).__init__()
    self.saved_args = None

  def execute(self, argument):
    self.saved_args = _save_args(argument.args)
    return step_result(True, None)

  def on_tag_changed(self):
    pass
  
  @classmethod
  def parse_step_args(clazz, packager_env, args):
    keys = [ key for key in args.keys() if key.startswith('desc2_') ]
    return { key: args[key] for key in keys }

class sample_step_save_args3(Step):
  def __init__(self):
    super(sample_step_save_args3, self).__init__()
    self.saved_args = None

  def execute(self, argument):
    self.saved_args = _save_args(argument.args)
    return step_result(True, None)

  def on_tag_changed(self):
    pass
  
  @classmethod
  def parse_step_args(clazz, packager_env, args):
    keys = [ key for key in args.keys() if key.startswith('desc3_') ]
    return { key: args[key] for key in keys }

class sample_step_fake_success(Step):
  def __init__(self):
    super(sample_step_fake_success, self).__init__()

  def execute(self, argument):
    fake_success = argument.args['fake_success']
    if fake_success:
      fake_message = ''
    else:
      fake_message = 'step %s failed' % (argument.args['fake_name'])
    return step_result(fake_success, fake_message)

  def on_tag_changed(self):
    pass
  
class sample_step_fake_output1(Step):
  def __init__(self):
    super(sample_step_fake_output1, self).__init__()

  def execute(self, argument):
    fake_output = argument.args.get('fake_output', None)
    return step_result(True, output = fake_output)

  def on_tag_changed(self):
    pass
  
class sample_step_fake_output2(Step):
  def __init__(self):
    super(sample_step_fake_output2, self).__init__()

  def execute(self, argument):
    fake_output = argument.args.get('fake_output2', None)
    return step_result(True, output = fake_output)

  def on_tag_changed(self):
    pass
  
class sample_step_fake_output3(Step):
  def __init__(self):
    super(sample_step_fake_output3, self).__init__()

  def execute(self, argument):
    fake_output = argument.args.get('fake_output3', None)
    return step_result(True, output = fake_output)

  def on_tag_changed(self):
    pass
  
class sample_step_save_args_with_global_args1(sample_step_save_args1):
  __step_global_args__ = {
    'global_arg10': '10',
    'global_arg11': '11',
  }
  def __init__(self):
    super(sample_step_save_args_with_global_args1, self).__init__()
    
class sample_step_save_args_with_global_args2(sample_step_save_args2):
  __step_global_args__ = {
    'global_arg12': '12',
    'global_arg13': '13',
  }
  def __init__(self):
    super(sample_step_save_args_with_global_args2, self).__init__()
    
class sample_step_save_args_with_global_args3(sample_step_save_args3):
  __step_global_args__ = {
    'global_arg14': '14',
    'global_arg15': '15',
  }
  def __init__(self):
    super(sample_step_save_args_with_global_args3, self).__init__()
