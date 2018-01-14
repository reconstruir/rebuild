#include "template2.h"

int template2_foo(int x)
{
  return template1_foo(1000);
}

int template2_bar(int x)
{
  return template2_foo(2000);
}

