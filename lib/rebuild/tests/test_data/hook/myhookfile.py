
def _private():
  return 'foo'

def my_hook_func(arg):
  assert arg
  global _private
  return _private() + ':' + arg
