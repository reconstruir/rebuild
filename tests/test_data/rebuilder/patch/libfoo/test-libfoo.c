#include <libfoo/foo.h>
#include <libfoo/bar.h>
#include <stdio.h>

int main()
{
  int EXPECTED_X = 666;
  int x = foo_baz(0);
  if (x != EXPECTED_X) {
    fprintf(stderr, "error x is %d instead of %d", x, EXPECTED_X);
    return 1;
  }
  return 0;
}
