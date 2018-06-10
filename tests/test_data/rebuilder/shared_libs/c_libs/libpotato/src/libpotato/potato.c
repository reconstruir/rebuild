#include "potato.h"
#include "common.h"
#include <libstarch/amylose.h>
#include <libstarch/amylopectin.h>

int potato_foo()
{
  return potato_common_foo() + amylose_bar(0) + amylopectin_bar(0) + 900;
}
