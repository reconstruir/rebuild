
def rebuild_recipes(env):
  configure_env = [
    'linux: CFLAGS="-I${REBUILD_REQUIREMENTS_INCLUDE_DIR} -std=gnu99" LDFLAGS=\"-L${REBUILD_REQUIREMENTS_LIB_DIR}\"',
  ]
  return env.args(
    properties = env.args(
      name = 'fructose',
      version = '3.4.5-6',
      category = 'lib',
      env_vars = {
        'FRUCTOSE_FOO': '666',
      }
    ),
    env_vars = [
      'all: FRUCTOSE_FOO=666',
    ],
    requirements = [
    ],
    steps = [
      'step_autoconf', {
        'configure_env': configure_env,
      }
    ],
  )
