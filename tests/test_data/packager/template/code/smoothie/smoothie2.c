#include "smoothie2.h"

#include <fiber1/fiber1.h>

int smoothie2_foo(int x)
{
  return fiber1_foo(1000) + smoothie1_foo(1000);
}

int smoothie2_bar(int x)
{
  return fiber2_foo(1600) + smoothie2_foo(2000);
}
