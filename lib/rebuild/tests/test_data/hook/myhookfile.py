
def _private():
  return 'myhookprivate'

def my_hook_func(script, env, args):
  assert script
  assert env
  assert args
  global _private
  return _private() + ':' + script + ':' + env + ':' + args
