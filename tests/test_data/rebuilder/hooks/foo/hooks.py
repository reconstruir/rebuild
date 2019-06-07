#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from rebuild.recipe.value import value_hook

class _test_hook1(value_hook):
    
  def execute(self, script, env):
    import os.path as path
    from bes.fs.file_replace import file_replace
    f = path.join(script.staged_files_bin_dir, 'foo.py')
    file_replace.replace(f, { '@FOO@': 'hook1' }, word_boundary = True)
    return self.result(True)
  
class _test_hook2(value_hook):
    
  def execute(self, script, env):
    import os.path as path
    from bes.fs.file_replace import file_replace
    f = path.join(script.staged_files_bin_dir, 'foo.py')
    file_replace.replace(f, { '@BAR@': 'hook2' }, word_boundary = True)
    return self.result(True)
