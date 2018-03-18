
def rebuild_recipes(env):

  tests = [
    'all: test-libpotato.c',
  ]

  pc_files = [
    'all: libpotato.pc',
  ]
  
  return env.args(
    properties = env.args(
      name = 'libpotato',
      version = '1.0.0',
      category = 'lib',
    ),
    steps = [
      'step_setup', {
        'copy_source_to_build_dir': True,
        'tarball_source_dir_override': 'src',
      },
      'step_make',
      'step_make_install',
      'step_post_install', {
        'tests': tests,
        'skip_binary_third_party_prefix': True,
        'pc_files': pc_files,
      }
    ],
  )
