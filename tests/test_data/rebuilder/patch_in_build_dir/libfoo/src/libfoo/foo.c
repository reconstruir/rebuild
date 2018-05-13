#include "foo.h"
#include "common.h"

int foo_foo(int x)
{
  return foo_common_foo() + 100;
}

int foo_bar(int x)
{
  return 200;
}

