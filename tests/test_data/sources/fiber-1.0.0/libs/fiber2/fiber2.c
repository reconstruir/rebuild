#include "fiber2.h"

int fiber2_foo(int x)
{
  return fiber1_foo(1000);
}

int fiber2_bar(int x)
{
  return fiber2_foo(2000);
}

