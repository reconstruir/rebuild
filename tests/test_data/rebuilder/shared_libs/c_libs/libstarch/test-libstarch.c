#include <libstarch/amylose.h>
#include <libstarch/amylopectin.h>
#include <assert.h>

int main()
{
  assert( 600 == amylopectin_foo(0) );
  assert( 700 == amylopectin_bar(0) );
  return 0;
}
