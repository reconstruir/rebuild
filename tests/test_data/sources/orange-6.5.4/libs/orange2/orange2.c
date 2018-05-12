#include "orange2.h"

#include <fiber1/fiber1.h>

int orange2_foo(int x)
{
  return fiber1_foo(1000) + orange1_foo(1000);
}

int orange2_bar(int x)
{
  return fiber2_foo(1600) + orange2_foo(2000);
}

