#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.step import step

class _custom_step_make_foo(step):
  'make a foo.'
    
  def __init__(self):
    super(self.__class__, self).__init__()

  CONTENT = 'def foo_func1(x): return x + 10\n'
    
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    import os.path as path
    from bes.fs import file_util
    foo_filename = path.join(script.build_dir, 'foo.py')
    file_util.save(foo_filename, content = self.CONTENT, mode = 0o644)
    return self.result(True, outputs = { 'foo_filename': foo_filename })

class _custom_step_install_foo(step):
  'install a foo.'
  
  def __init__(self):
    super(self.__class__, self).__init__()
  
  #@abstractmethod
  def execute(self, script, env, values, inputs):
    import os.path as path
    from rebuild.tools import install
    from bes.fs import file_util
    src_filename = inputs.get('foo_filename')
    install.install(src_filename, script.python_lib_dir, mode = 0o644)
    file_util.save(path.join(script.python_lib_dir, '__init__.py'), content = '', mode = 0o644)
    return self.result(True)
