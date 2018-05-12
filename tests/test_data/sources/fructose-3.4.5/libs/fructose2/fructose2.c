#include "fructose2.h"

int fructose2_foo(int x)
{
  return fructose1_foo(1000);
}

int fructose2_bar(int x)
{
  return fructose2_foo(2000);
}

