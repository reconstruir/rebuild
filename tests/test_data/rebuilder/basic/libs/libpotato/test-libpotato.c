#include <libpotato/potato.h>
#include <stdio.h>

int main()
{
  int EXPECTED_X = 1801;
  int x = potato_foo();
  if (x != EXPECTED_X) {
    fprintf(stderr, "error x is %d instead of %d", x, EXPECTED_X);
    return 1;
  }
  return 0;
}
