#include <libpotato/amylose.h>
#include <libpotato/amylopectin.h>
#include <stdio.h>

int main()
{
  int EXPECTED_X = 701;
  int x = amylose_foo(0) + amylopectin_foo(0);
  if (x != EXPECTED_X) {
    fprintf(stderr, "error x is %d instead of %d", x, EXPECTED_X);
    return 1;
  }
  return 0;
}
