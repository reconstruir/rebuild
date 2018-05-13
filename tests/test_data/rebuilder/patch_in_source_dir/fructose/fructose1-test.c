#include <stdio.h>
#include <assert.h>

#include <fructose1/fructose1.h>

int main()
{
  assert( 100 == fructose1_foo(0) );
  assert( 200 == fructose1_bar(0) );
  assert( 300 == fructose1_baz(0) );
  return 0;
}
