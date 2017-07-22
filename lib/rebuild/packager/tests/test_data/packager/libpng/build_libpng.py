def rebuild_recipes(env):
  configure_env = [
    'all: CFLAGS="$REBUILD_REQUIREMENTS_CFLAGS ${REBUILD_COMPILE_CFLAGS}" LDFLAGS=$REBUILD_REQUIREMENTS_LDFLAGS PNG_COPTS=$REBUILD_REQUIREMENTS_CFLAGS',
  ]
  configure_flags = [
    'all: --enable-static --disable-shared',
    'linux: --with-pic',
  ]
  patches = [
    'all: reb-libpng-zlib.patch',
  ]
  tests = [
    'desktop: reb-libpng-test-cpp-link.cpp reb-libpng-test-process.c',
  ]
  return env.args(
    properties = env.args(
      name = 'libpng',
      version = '1.6.28',
      revision = '1',
      category = 'lib',
      export_compilation_flags_requirements = [
        'all: zlib',
      ]
    ),
    requirements = [
      'all: zlib >= 1.2.8',
    ],
    steps = [
      step_autoconf, {
        'patches': patches,
        'configure_env': configure_env,
        'configure_flags': configure_flags,
        'tests': tests,
      },
    ],
  )
