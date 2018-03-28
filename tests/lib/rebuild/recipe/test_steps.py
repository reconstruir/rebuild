#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import compound_step, step, step_result

class step_foo(step):
  def __init__(self):
    super(step_foo, self).__init__()

  @classmethod
  def define_args(clazz):
    return '''
    foo_flags key_values
    foo_env string_list
    foo_script string
    need_something bool
    patches string_list
    tests string_list
    '''
    
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
  def define_args(clazz):
    return 'bool_value bool'
  
  def execute(self, script, env, args):
    return step_result(True)

class step_takes_int(step):
  def __init__(self):
    super(step_takes_int, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'int_value int'
  
  def execute(self, script, env, args):
    return step_result(True)
    
class step_takes_string(step):
  def __init__(self):
    super(step_takes_string, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'string_value string'
  
  def execute(self, script, env, args):
    return step_result(True)
    
class step_takes_string_list(step):
  def __init__(self):
    super(step_takes_string_list, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'string_list_value string_list'
  
  def execute(self, script, env, args):
    return step_result(True)
    
class step_takes_key_values(step):
  def __init__(self):
    super(step_takes_key_values, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'key_values_value key_values'
  
  def execute(self, script, env, args):
    return step_result(True)

class step_takes_hook_list(step):
  def __init__(self):
    super(step_takes_hook_list, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'hook_list_value hook_list'
  
  def execute(self, script, env, args):
    return step_result(True)
  
class step_takes_file_list(step):
  def __init__(self):
    super(step_takes_file_list, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'file_list_value file_list'
  
  def execute(self, script, env, args):
    return step_result(True)

class step_takes_file(step):
  def __init__(self):
    super(step_takes_file, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'file_value file'
  
  def execute(self, script, env, args):
    return step_result(True)
  
class step_takes_file_install_list(step):
  def __init__(self):
    super(step_takes_file_install_list, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'file_install_list_value file_install_list'
  
  def execute(self, script, env, args):
    return step_result(True)
  
class step_takes_all(step):
  def __init__(self):
    super(step_takes_all, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return '''
      bool_value         bool
      int_value          int
      string_value       string
      string_list_value  string_list
      key_values_value   key_values
    '''
  
  def execute(self, script, env, args):
    return step_result(True)

class step_compound(compound_step):
  __steps__ = [
    step_takes_bool,
    step_takes_int,
    step_takes_string,
    step_takes_string_list,
    step_takes_key_values
  ]

class step_apple(step):
  def __init__(self):
    super(step_apple, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return '''
    apple_bool_value bool
    apple_int_value int
    apple_string_value string
    apple_string_list_value string_list
    apple_key_values_value key_values
    '''
  
  def execute(self, script, env, args):
    return step_result(True)
  
class step_kiwi(step):
  def __init__(self):
    super(step_kiwi, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return '''
    kiwi_bool_value bool
    kiwi_int_value int
    kiwi_string_value string
    kiwi_string_list_value string_list
    kiwi_key_values_value key_values
    '''
  
  def execute(self, script, env, args):
    return step_result(True)

class step_pear(step):
  def __init__(self):
    super(step_pear, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return '''
    pear_bool_value bool
    pear_int_value int
    pear_string_value string
    pear_string_list_value string_list
    pear_key_values_value key_values
    '''
  
  def execute(self, script, env, args):
    return step_result(True)
  
  
