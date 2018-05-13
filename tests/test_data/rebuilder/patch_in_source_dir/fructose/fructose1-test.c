#include <stdio.h>
#include <assert.h>

#include <fructose1/fructose1.h>

int main()
{
  assert( 100 == fructose1_foo(1) );
  assert( 200 == fructose1_bar(1) );
  assert( 300 == fructose1_baz(1) );
  return 0;
}
