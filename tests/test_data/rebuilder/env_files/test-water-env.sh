#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/rebuild_framework.sh

function test_water_env()
{
  rebuild_assert "[ '$LIBCARB_ENV1' = '' ]"
  rebuild_assert "[ '$LIBCARB_ENV2' = '' ]"
  rebuild_assert "[ '$LIBFIBER_ENV1' = '' ]"
  rebuild_assert "[ '$LIBFIBER_ENV2' = '' ]"
  rebuild_assert "[ '$LIBFRUIT_ENV1' = '' ]"
  rebuild_assert "[ '$LIBFRUIT_ENV2' = '' ]"
  rebuild_assert "[ '$LIBWATER_ENV1' = 'water_env1' ]"
  rebuild_assert "[ '$LIBWATER_ENV2' = 'water_env2' ]"
}

rebuild_testing_run_unit_tests
