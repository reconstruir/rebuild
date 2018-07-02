include $(_TEST_MAKE_DIR)/common.mk

MAKE_STATIC_LIB = libpapaya.a
MAKE_STATIC_LIB_OBJS = libpapaya/papaya.o libpapaya/common.o

all: $(MAKE_STATIC_LIB) papaya_prog1_main

LIBPOTATO_HEADERS = libpapaya/papaya.h libpapaya/common.h

POTATO_PROG1_MAIN_OBJS = programs/papaya_prog1/papaya_prog1_main.o papaya_gen.o
POTATO_PROG1_MAIN_LIBS = -lpapaya

include $(_TEST_MAKE_DIR)/static_lib.mk

papaya_prog1_main: $(POTATO_PROG1_MAIN_OBJS) $(MAKE_STATIC_LIB)
	$(CC) -o $@ $(POTATO_PROG1_MAIN_OBJS) $(LDFLAGS) $(LOCAL_LDFLAGS) $(POTATO_PROG1_MAIN_LIBS)

papaya_gen.h:
	echo POTOFUCK $(CODEGEN_ENV1) $(CODEGEN_ENV2)
	codegen.py papaya_gen --header myfunc 667 > $@

papaya_gen.c: papaya_gen.h
	codegen.py papaya_gen myfunc 667 > $@

clean:
	rm -f $(MAKE_STATIC_LIB_OBJS) $(POTATO_PROG1_MAIN_OBJS) $(MAKE_STATIC_LIB) papaya_prog1_main

install: papaya_prog1_main $(MAKE_STATIC_LIB) $(LIBPOTATO_HEADERS)
	mkdir -p $(prefix)/bin
	mkdir -p $(prefix)/lib
	mkdir -p $(prefix)/include/libpapaya
	install -m 755 papaya_prog1_main $(prefix)/bin
	install -m 644 $(MAKE_STATIC_LIB) $(prefix)/lib
	$(foreach header,$(LIBPOTATO_HEADERS),install -m 644 $(header) $(prefix)/include/libpapaya;)
