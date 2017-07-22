#include "water2.h"

int water2_foo(int x)
{
  return water1_foo(1000);
}

int water2_bar(int x)
{
  return water2_foo(2000);
}

