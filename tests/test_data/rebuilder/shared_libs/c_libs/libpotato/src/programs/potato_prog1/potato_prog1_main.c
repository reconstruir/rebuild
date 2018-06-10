#include <libpotato/potato.h>
#include <stdio.h>

extern int potato_gen_myfunc();

int main()
{
  printf("potato_prog1_main:%d\n", potato_foo(0) + potato_gen_myfunc());
  return 0;
}
