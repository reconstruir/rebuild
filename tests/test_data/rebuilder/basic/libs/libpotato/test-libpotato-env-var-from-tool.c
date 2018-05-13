#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

int main()
{
  assert( 0 == strcmp("foo", getenv("TBAR_ENV1")) );
  assert( 0 == strcmp("bar", getenv("TBAR_ENV2")) );
  return 0;
}
