#include <stdio.h>

#include <fiber1/fiber1.h>
#include <fiber2/fiber2.h>

int main()
{
  printf("fiber1_foo() => %d\n", fiber1_foo(1));
  printf("fiber1_bar() => %d\n", fiber1_bar(1));
  printf("fiber2_foo() => %d\n", fiber2_foo(1));
  printf("fiber2_bar() => %d\n", fiber2_bar(1));

  return 0;
}
