#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.sh

function test_carb_env()
{
  rebuild_assert "[ '$LIBCARB_ENV1' = 'carb_env1' ]"
  rebuild_assert "[ '$LIBCARB_ENV2' = 'carb_env2' ]"
  rebuild_assert "[ '$LIBFIBER_ENV1' = '' ]"
  rebuild_assert "[ '$LIBFIBER_ENV2' = '' ]"
  rebuild_assert "[ '$LIBFRUIT_ENV1' = '' ]"
  rebuild_assert "[ '$LIBFRUIT_ENV2' = '' ]"
  rebuild_assert "[ '$LIBWATER_ENV1' = '' ]"
  rebuild_assert "[ '$LIBWATER_ENV2' = '' ]"
}

bes_testing_run_unit_tests
