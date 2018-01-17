
def rebuild_recipes(env):
  return env.args(
    properties = env.args(
      name = 'fructose',
      version = '3.4.5-6',
      category = 'lib',
      env_vars = {
        'FRUCTOSE_FOO': '666',
      }
    ),
    requirements = [
    ],
    steps = [
      'step_autoconf',
    ],
  )
