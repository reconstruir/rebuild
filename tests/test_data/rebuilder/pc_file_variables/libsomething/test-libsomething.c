#include <libsomething/foo.h>
#include <libsomething/bar.h>
#include <assert.h>

int main()
{
  assert( 701 == something_foo(0) + bar_foo(0) );
  return 0;
}
