#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step.compound_step import compound_step
from rebuild.step.step import step
from rebuild.step.step_result import step_result

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
    values = self.recipe.resolve_values(env.config.build_target.system)
    foo_flags = values.get('foo_flags')
    foo_env = values.get('foo_env')
    return step_result(True)

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

class step_takes_hook(step):
  def __init__(self):
    super(step_takes_hook, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'hook_value hook'
  
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
  
class step_takes_install_file(step):
  def __init__(self):
    super(step_takes_install_file, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'install_file_value install_file'
  
  def execute(self, script, env, args):
    return step_result(True)

class step_takes_git_address(step):
  def __init__(self):
    super(step_takes_git_address, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return 'git_address_value git_address'
  
  def execute(self, script, env, args):
    return step_result(True)
  
class step_takes_all(step):
  def __init__(self):
    super(step_takes_all, self).__init__()
    
  @classmethod
  def define_args(clazz):
    return '''
      bool_value              bool
      file_value              file
      install_file_value      install_file
      file_list_value         file_list
      hook_value              hook
      int_value               int
      key_values_value        key_values
      string_value            string
      string_list_value       string_list
      git_address_value       git_address
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
