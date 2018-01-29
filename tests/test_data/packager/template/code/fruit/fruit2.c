#include "fruit2.h"

#include <fiber1/fiber1.h>

int fruit2_foo(int x)
{
  return fiber1_foo(1000) + fruit1_foo(1000);
}

int fruit2_bar(int x)
{
  return fiber2_foo(1600) + fruit2_foo(2000);
}
