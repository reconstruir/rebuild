#include <stdio.h>

extern "C" int test(int foo)
{
  printf("foo(%d)\n", foo);
  return 666;
}
