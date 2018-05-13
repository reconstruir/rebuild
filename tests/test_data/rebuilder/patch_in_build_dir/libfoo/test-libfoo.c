#include <libfoo/foo.h>
#include <libfoo/bar.h>
#include <assert.h>

int main()
{
  assert( 666 == foo_baz(0) );
  return 0;
}
