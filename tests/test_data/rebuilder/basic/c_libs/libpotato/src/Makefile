include $(_TEST_MAKE_DIR)/common.mk

MAKE_STATIC_LIB = libpotato.a
MAKE_STATIC_LIB_OBJS = libpotato/potato.o libpotato/common.o

ifdef REBUILD_NO_PROGRAMS
	programs=
else
	programs=potato_prog1_main
endif

all: $(MAKE_STATIC_LIB) $(programs)

LIBPOTATO_HEADERS = libpotato/potato.h libpotato/common.h

POTATO_PROG1_MAIN_OBJS = programs/potato_prog1/potato_prog1_main.o potato_gen.o
POTATO_PROG1_MAIN_LIBS = -lpotato -lstarch

include $(_TEST_MAKE_DIR)/static_lib.mk

potato_prog1_main: $(POTATO_PROG1_MAIN_OBJS) $(MAKE_STATIC_LIB)
	$(CC) -o $@ $(POTATO_PROG1_MAIN_OBJS) $(LDFLAGS) $(LOCAL_LDFLAGS) $(POTATO_PROG1_MAIN_LIBS)

potato_gen.h:
	tbar_code_gen.py potato_gen --header myfunc 667 > $@

potato_gen.c: potato_gen.h
	tbar_code_gen.py potato_gen myfunc 667 > $@

clean:
	rm -f $(MAKE_STATIC_LIB_OBJS) $(POTATO_PROG1_MAIN_OBJS) $(MAKE_STATIC_LIB) $(programs)

install: $(programs) $(MAKE_STATIC_LIB) $(LIBPOTATO_HEADERS)
	mkdir -p $(prefix)/bin
	mkdir -p $(prefix)/lib
	mkdir -p $(prefix)/include/libpotato
ifndef REBUILD_NO_PROGRAMS
	install -m 755 $(programs) $(prefix)/bin
endif
	install -m 644 $(MAKE_STATIC_LIB) $(prefix)/lib
	$(foreach header,$(LIBPOTATO_HEADERS),install -m 644 $(header) $(prefix)/include/libpotato;)
