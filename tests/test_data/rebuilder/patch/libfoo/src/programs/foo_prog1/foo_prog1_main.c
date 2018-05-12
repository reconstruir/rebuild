#include <libfoo/foo.h>
#include <libfoo/bar.h>
#include <stdio.h>
#include <stdlib.h>

extern char **environ;

int main()
{
  for (unsigned int i = 0; environ[i] != NULL; i++) {
    printf("%s\n", environ[i]);
  }
  return 0;
}
