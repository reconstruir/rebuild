prefix=/usr/local
CC=clang
AR=ar
AR_FLAGS=r
LOCAL_CFLAGS=-I.
LOCAL_LDFLAGS=

%.o: %.c
	$(CC) $(CFLAGS) $(LOCAL_CFLAGS) -c $< -o $@

all: libpotato.so potato_prog1_main

LIBSTARCH_OBJS = libpotato/potato.o libpotato/common.o
LIBSTARCH_HEADERS = libpotato/potato.h libpotato/common.h

libpotato.a: $(LIBSTARCH_OBJS)
	$(AR) $(AR_FLAGS) $@ $^

libpotato.so: libpotato.a
	$(CC) -shared $(LOCAL_LDFLAGS) $@ -o $^

STARCH_PROG1_MAIN_OBJS = programs/potato_prog1/potato_prog1_main.o potato_gen.o
STARCH_PROG1_MAIN_LIBS = -lstarch

potato_prog1_main: $(STARCH_PROG1_MAIN_OBJS) libpotato.so
	$(CC) -o $@ $^ $(LDFLAGS) $(STARCH_PROG1_MAIN_LIBS)

potato_gen.h:
	tbar_code_gen.py potato_gen --header myfunc 667 > $@

potato_gen.c: potato_gen.h
	tbar_code_gen.py potato_gen myfunc 667 > $@

clean:
	rm -f $(LIBSTARCH_OBJS) $(STARCH_PROG1_MAIN_OBJS) libpotato.so potato_prog1_main

install: potato_prog1_main libpotato.so $(LIBSTARCH_HEADERS)
	mkdir -p $(prefix)/bin
	mkdir -p $(prefix)/lib
	mkdir -p $(prefix)/include/libpotato
	install -m 755 potato_prog1_main $(prefix)/bin
	install -m 644 libpotato.so $(prefix)/lib
	$(foreach header,$(LIBSTARCH_HEADERS),install -m 644 $(header) $(prefix)/include/libpotato;)
