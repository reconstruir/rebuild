//#include <config.h>
#include <stdio.h>

int main(int argc, char* argv[])
{
  for (unsigned int i = 1; i < argc; i++) {
    printf("%s\n", argv[i]);
  }
  return 0;
}
