#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.bash

function test_water_env()
{
  bes_assert "[ '$LIBCARB_ENV1' = '' ]"
  bes_assert "[ '$LIBCARB_ENV2' = '' ]"
  bes_assert "[ '$LIBFIBER_ENV1' = '' ]"
  bes_assert "[ '$LIBFIBER_ENV2' = '' ]"
  bes_assert "[ '$LIBFRUIT_ENV1' = '' ]"
  bes_assert "[ '$LIBFRUIT_ENV2' = '' ]"
  bes_assert "[ '$LIBWATER_ENV1' = 'water_env1' ]"
  bes_assert "[ '$LIBWATER_ENV2' = 'water_env2' ]"
}

bes_testing_run_unit_tests
