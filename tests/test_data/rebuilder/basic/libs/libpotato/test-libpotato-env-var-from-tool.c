#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

int main()
{
  const char* env_var1;
  const char* env_var2;
  
  env_var1 = getenv("TBAR_ENV1");
  if (env_var1 == NULL) {
    fprintf(stderr, "TBAR_ENV1 is not set.\n");
    return 1;
  }
  if (strcmp(env_var1, "foo") != 0) {
    fprintf(stderr, "TBAR_ENV1 should be \"foo\" instead of \"%s\"\n", env_var1);
    return 1;
  }

  env_var2 = getenv("TBAR_ENV2");
  if (env_var2 == NULL) {
    fprintf(stderr, "TBAR_ENV2 is not set.\n");
    return 1;
  }
  if (strcmp(env_var2, "bar") != 0) {
    fprintf(stderr, "TBAR_ENV2 should be \"bar\" instead of \"%s\"\n", env_var2);
    return 1;
  }
  
  return 0;
}
