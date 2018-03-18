
def rebuild_recipes(env):

  tests = [
    'all: test-libstarch.c',
  ]

  return env.args(
    properties = env.args(
      name = 'libstarch',
      version = '1.0.0',
      category = 'lib',
    ),
    steps = [
      'step_setup', {
        'no_tarballs': True,
        'copy_source_to_build_dir': True,
      },
      'step_make',
      'step_make_install',
      'step_post_install', {
        'tests': tests,
        'skip_binary_third_party_prefix': True,
      }
    ],
  )
