
def _private():
  return 'foo'

def my_hook_func(arg):
  assert arg
  assert isinstance(arg, basestring)
  global _private
  return _private() + ':' + arg
