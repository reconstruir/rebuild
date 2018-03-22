def rebuild_recipes(env):
  return env.args(
    properties = env.args(
      name = 'libjpeg',
      version = '9a',
      revision = '1',
    ),
    steps = [
      step_setup,
      step_autoconf_configure,
      step_shell, { 'cmd': 'make V=1' },
      step_shell, { 'cmd': 'make install prefix=$REBUILD_STAGE_PREFIX_DIR V=1' },
      step_artifact_create,
    ],
  )
