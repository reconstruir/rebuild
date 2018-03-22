
def rebuild_recipes(env):

  tests = [
    'all: test-tfoo.sh',
  ]

  return env.args(
    properties = env.args(
      name = 'tfoo',
      version = '1.0.0',
    ),
    steps = [
      'step_setup', {
        'no_tarballs': True,
      },
      'step_post_install', {
        'install_files': [ 'all: files/bin/tfoo.py bin/tfoo.py' ],
        'tests': tests,
        'skip_binary_third_party_prefix': True,
      }
    ],
  )
