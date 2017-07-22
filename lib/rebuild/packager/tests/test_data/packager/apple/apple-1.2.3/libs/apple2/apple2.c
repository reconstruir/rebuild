#include "apple2.h"

#include <fiber1/fiber1.h>

int apple2_foo(int x)
{
  return fiber1_foo(1000) + apple1_foo(1000);
}

int apple2_bar(int x)
{
  return fiber2_foo(1600) + apple2_foo(2000);
}

