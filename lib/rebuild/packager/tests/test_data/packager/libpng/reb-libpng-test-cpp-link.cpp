#include <png.h>
#include <stdio.h>

int main(int argc, char* argv[])
{
  png_uint_32 png_version = png_access_version_number();
  printf("%s: png_version=%d\n", argv[0], png_version);
  return 0;
}
