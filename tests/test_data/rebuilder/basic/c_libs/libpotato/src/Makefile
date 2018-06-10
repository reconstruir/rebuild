include $(_TEST_MAKE_DIR)/common.mk

all: libpotato.a potato_prog1_main

LIBPOTATO_OBJS = libpotato/potato.o libpotato/common.o
LIBPOTATO_HEADERS = libpotato/potato.h libpotato/common.h

libpotato.a: $(LIBPOTATO_OBJS)
	$(AR) $(AR_FLAGS) $@ $^

POTATO_PROG1_MAIN_OBJS = programs/potato_prog1/potato_prog1_main.o potato_gen.o
POTATO_PROG1_MAIN_LIBS = -lpotato -lstarch

potato_prog1_main: $(POTATO_PROG1_MAIN_OBJS) libpotato.a
	$(CC) -o $@ $(POTATO_PROG1_MAIN_OBJS) $(LDFLAGS) $(LOCAL_LDFLAGS) $(POTATO_PROG1_MAIN_LIBS)

potato_gen.h:
	tbar_code_gen.py potato_gen --header myfunc 667 > $@

potato_gen.c: potato_gen.h
	tbar_code_gen.py potato_gen myfunc 667 > $@

clean:
	rm -f $(LIBPOTATO_OBJS) $(POTATO_PROG1_MAIN_OBJS) libpotato.a potato_prog1_main

install: potato_prog1_main libpotato.a $(LIBPOTATO_HEADERS)
	mkdir -p $(prefix)/bin
	mkdir -p $(prefix)/lib
	mkdir -p $(prefix)/include/libpotato
	install -m 755 potato_prog1_main $(prefix)/bin
	install -m 644 libpotato.a $(prefix)/lib
	$(foreach header,$(LIBPOTATO_HEADERS),install -m 644 $(header) $(prefix)/include/libpotato;)
