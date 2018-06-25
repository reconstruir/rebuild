#include <libpapaya/papaya.h>
#include <stdio.h>

extern int papaya_gen_myfunc();

int main()
{
  printf("papaya_prog1_main:%d\n", papaya_foo(0) + papaya_gen_myfunc());
  return 0;
}
