
def rebuild_recipes(env):
  tests = [ 'all: orange-test.c' ]
  configure_env = [
    'all: CFLAGS=-I${REBUILD_REQUIREMENTS_INCLUDE_DIR} LDFLAGS=\"-L${REBUILD_REQUIREMENTS_LIB_DIR}\"',
  ]
  return env.args(
    properties = env.args(
      name = 'orange',
      version = '6.5.4-3',
      category = 'lib',
    ),
    instructions = '''
name: liborange1
CFLAGS: -I${REBUILD_PACKAGE_PREFIX}/include
LDFLAGS: -L${REBUILD_PACKAGE_PREFIX}/lib
LIBS: -lorange1
requires: libfructose1

name: liborange2
CFLAGS: -I${REBUILD_PACKAGE_PREFIX}/include
        -I${REBUILD_PACKAGE_PREFIX}/include/caca
LDFLAGS: -L${REBUILD_PACKAGE_PREFIX}/lib
LIBS: -lorange2
requires: libfiber1

name: orange
requires: liborange2 liborange1
    ''',
    requirements = [
      "all: fructose >= 3.4.5-6", "all: fiber >= 1.0.0-0"
    ],
    build_requirements = [
    ],
    steps = [
      step_autoconf, {
        'tests': tests,
        'configure_env': configure_env,
      },
    ],
  )
