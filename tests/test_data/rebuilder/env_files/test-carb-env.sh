#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.sh

function test_carb_env()
{
  bes_assert "[ '$LIBCARB_ENV1' = 'carb_env1' ]"
  bes_assert "[ '$LIBCARB_ENV2' = 'carb_env2' ]"
  bes_assert "[ '$LIBFIBER_ENV1' = '' ]"
  bes_assert "[ '$LIBFIBER_ENV2' = '' ]"
  bes_assert "[ '$LIBFRUIT_ENV1' = '' ]"
  bes_assert "[ '$LIBFRUIT_ENV2' = '' ]"
  bes_assert "[ '$LIBWATER_ENV1' = '' ]"
  bes_assert "[ '$LIBWATER_ENV2' = '' ]"
}

bes_testing_run_unit_tests
