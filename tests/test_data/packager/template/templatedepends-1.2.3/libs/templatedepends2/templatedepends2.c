#include "templatedepends2.h"

#include <fiber1/fiber1.h>

int templatedepends2_foo(int x)
{
  return fiber1_foo(1000) + templatedepends1_foo(1000);
}

int templatedepends2_bar(int x)
{
  return fiber2_foo(1600) + templatedepends2_foo(2000);
}

