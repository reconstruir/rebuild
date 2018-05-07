#include "foo.h"
#include "common.h"

int something_foo(int x)
{
  return something_common_foo() + 100;
}

int something_bar(int x)
{
  return 200;
}

