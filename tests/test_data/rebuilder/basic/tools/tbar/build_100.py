
def rebuild_recipes(env):

  tests = [
    'all: test-tbar.sh test-tbar-env-var.sh',
  ]

  return env.args(
    properties = env.args(
      name = 'tbar',
      version = '1.0.0',
      category = 'tool',
      env_vars = {
        'TBAR_ENV1': 'foo',
        'TBAR_ENV2': 'bar',
      }
    ),
    requirements = [
      'all: TOOL tfoo >= 1.0.0',
    ],
    env_vars = [
      'all: TBAR_ENV1=foo TBAR_ENV2=bar',
    ],
    steps = [
      'step_setup', {
        'no_tarballs': True,
      },
      'step_post_install', {
        'install_files': [ 'all: files/bin/tbar.py bin/tbar.py files/bin/tbar_code_gen.py bin/tbar_code_gen.py' ],
        'tests': tests,
        'skip_binary_third_party_prefix': True,
      }
    ],
  )
