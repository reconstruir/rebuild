#include <orange1/orange1.h>
#include <orange2/orange2.h>
#include <assert.h>

int main()
{
  assert( 1801 == orange1_foo(1) )
  assert( 1801 == orange1_bar(1) )
  assert( 1801 == orange2_foo(1) )
  assert( 1801 == orange2_bar(1) )
  return 0;
}
