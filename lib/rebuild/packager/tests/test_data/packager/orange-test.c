#include <stdio.h>

#include <orange1/orange1.h>
#include <orange2/orange2.h>

int main()
{
  printf("orange1_foo() => %d\n", orange1_foo(1));
  printf("orange1_bar() => %d\n", orange1_bar(1));
  printf("orange2_foo() => %d\n", orange2_foo(1));
  printf("orange2_bar() => %d\n", orange2_bar(1));

  return 0;
}
