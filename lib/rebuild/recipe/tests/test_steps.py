#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step_manager import compound_step, step, step_argspec, step_result

class step_foo(step):
  def __init__(self):
    super(step_foo, self).__init__()

  @classmethod
  def argspec(clazz):
    return {
      'foo_flags': step_argspec.KEY_VALUES,
      'foo_env': step_argspec.STRING_LIST,
      'foo_script': step_argspec.STRING,
      'need_something': step_argspec.BOOL,
      'patches': step_argspec.STRING_LIST,
      'tests': step_argspec.STRING_LIST,
    }
    
  def execute(self, script, env, args):
    foo_flags = args.get('foo_flags', [])
    assert isinstance(foo_flags, list)
    foo_env = args.get('foo_env', {})
    assert isinstance(configure_env, dict)
    return step_result(True)

  @classmethod
  def parse_step_args(clazz, script, env, args):
    return clazz.resolve_step_args_env_and_flags(script, args, 'foo_env', 'foo_flags')

class step_takes_bool(step):
  def __init__(self):
    super(step_takes_bool, self).__init__()
    
  @classmethod
  def argspec(clazz):
    return {
      'bool_value': step_argspec.BOOL
    }
  
  def execute(self, script, env, args):
    return step_result(True)

class step_takes_int(step):
  def __init__(self):
    super(step_takes_int, self).__init__()
    
  @classmethod
  def argspec(clazz):
    return {
      'int_value': step_argspec.INT
    }
  
  def execute(self, script, env, args):
    return step_result(True)
    
class step_takes_string(step):
  def __init__(self):
    super(step_takes_string, self).__init__()
    
  @classmethod
  def argspec(clazz):
    return {
      'string_value': step_argspec.STRING
    }
  
  def execute(self, script, env, args):
    return step_result(True)
    
class step_takes_string_list(step):
  def __init__(self):
    super(step_takes_string_list, self).__init__()
    
  @classmethod
  def argspec(clazz):
    return {
      'string_list_value': step_argspec.STRING_LIST
    }
  
  def execute(self, script, env, args):
    return step_result(True)
    
class step_takes_key_values(step):
  def __init__(self):
    super(step_takes_key_values, self).__init__()
    
  @classmethod
  def argspec(clazz):
    return {
      'key_values_value': step_argspec.KEY_VALUES
    }
  
  def execute(self, script, env, args):
    return step_result(True)

class step_takes_all(step):
  def __init__(self):
    super(step_takes_all, self).__init__()
    
  @classmethod
  def argspec(clazz):
    return {
      'bool_value': step_argspec.BOOL,
      'int_value': step_argspec.INT,
      'string_value': step_argspec.STRING,
      'string_list_value': step_argspec.STRING_LIST,
      'key_values_value': step_argspec.KEY_VALUES,
    }
  
  def execute(self, script, env, args):
    return step_result(True)

  
class step_multiple(compound_step):
  step_classes = [
    step_takes_bool,
    step_takes_int,
    step_takes_string,
    step_takes_string_list,
    step_takes_key_values
  ]
