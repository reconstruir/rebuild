prefix=/usr/local
CC=clang
AR=ar
AR_FLAGS=r
LOCAL_CFLAGS=-I.

%.o: %.c
	$(CC) $(CFLAGS) $(LOCAL_CFLAGS) -c $< -o $@

all: libfoo.a foo_prog1_main

LIBSTARCH_OBJS = libfoo/foo.o libfoo/bar.o libfoo/common.o
LIBSTARCH_HEADERS = libfoo/bar.h libfoo/foo.h libfoo/common.h

libfoo.a: $(LIBSTARCH_OBJS)
	$(AR) $(AR_FLAGS) $@ $^

STARCH_PROG1_MAIN_OBJS = programs/foo_prog1/foo_prog1_main.o

foo_prog1_main: $(STARCH_PROG1_MAIN_OBJS) libfoo.a
	$(CC) -o $@ $^

clean:
	rm -f $(LIBSTARCH_OBJS) $(STARCH_PROG1_MAIN_OBJS) libfoo.a foo_prog1_main

install: foo_prog1_main libfoo.a $(LIBSTARCH_HEADERS)
	mkdir -p $(prefix)/bin
	mkdir -p $(prefix)/lib
	mkdir -p $(prefix)/include/libfoo
	install -m 755 foo_prog1_main $(prefix)/bin
	install -m 644 libfoo.a $(prefix)/lib
	$(foreach header,$(LIBSTARCH_HEADERS),install -m 644 $(header) $(prefix)/include/libfoo;)
