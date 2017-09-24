#include <stdio.h>

#include <fructose1/fructose1.h>
#include <fructose2/fructose2.h>

int main()
{
  printf("fructose1_foo() => %d\n", fructose1_foo(1));
  printf("fructose1_bar() => %d\n", fructose1_bar(1));
  printf("fructose2_foo() => %d\n", fructose2_foo(1));
  printf("fructose2_bar() => %d\n", fructose2_bar(1));

  return 0;
}
