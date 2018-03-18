
def rebuild_recipes(env):

  tests = [
    'all: test-tbar.sh',
  ]

  return env.args(
    properties = env.args(
      name = 'tbar',
      version = '1.0.0',
      category = 'tool',
    ),
    requirements = [
      'all: TOOL tfoo >= 1.0.0',
    ],
    steps = [
      'step_setup', {
        'no_tarballs': True,
      },
      'step_post_install', {
        'install_files': [ 'all: files/bin/tbar.py bin/tbar.py' ],
        'tests': tests,
        'skip_binary_third_party_prefix': True,
      }
    ],
  )
