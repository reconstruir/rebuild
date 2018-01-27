#include "pear2.h"

#include <fiber1/fiber1.h>

int pear2_foo(int x)
{
  return fiber1_foo(1000) + pear1_foo(1000);
}

int pear2_bar(int x)
{
  return fiber2_foo(1600) + pear2_foo(2000);
}
