
def rebuild_recipes(env):
  tests = [
    'all: test-libpotato.c test-libpotato-env-var-from-tool.c',
  ]
  pc_files = [
    'all: libpotato.pc',
  ]
  make_env = [
    'all: CFLAGS="${REBUILD_REQUIREMENTS_CFLAGS}" LDFLAGS="${REBUILD_REQUIREMENTS_LDFLAGS}"'
  ]
  make_flags = [
    'all: ${REBUILD_COMPILE_ENVIRONMENT}',
  ]
  make_install_env = make_env
  make_install_flags = [
  ]
  return env.args(
    properties = env.args(
      name = 'libpotato',
      version = '1.0.0',
      export_compilation_flags_requirements = [
        'all: libstarch',
      ],
    ),
    requirements = [
      'all: RUN libstarch >= 1.0.0',
      'all: TOOL tbar >= 1.0.0',
    ],
    steps = [
      'step_setup', {
        'copy_source_to_build_dir': True,
        'tarball_source_dir_override': 'src',
      },
      'step_make', {
        'make_env': make_env, 'make_flags': make_flags,
      },
      'step_make_install', {
        'make_install_env': make_install_env, 'make_install_flags': make_install_flags,
      },
      'step_post_install', {
        'tests': tests,
        'skip_binary_third_party_prefix': True,
        'pc_files': pc_files,
      }
    ],
  )
