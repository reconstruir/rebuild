#include <stdio.h>
#include <fructose2/fructose2.h>
#include <assert.h>

int main()
{
  assert( 1100 == fructose2_foo(0) );
  assert( 3100 == fructose2_bar(0) );
  return 0;
}
