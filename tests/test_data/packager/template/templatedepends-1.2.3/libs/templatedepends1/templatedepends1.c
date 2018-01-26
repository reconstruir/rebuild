#include "templatedepends1.h"

#include <fructose1/fructose1.h>

int templatedepends1_foo(int x)
{
  return fructose1_foo(10000);
}

int templatedepends1_bar(int x)
{
  return fructose1_foo(10200);
}

