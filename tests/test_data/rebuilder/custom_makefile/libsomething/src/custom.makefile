prefix=/usr/local
CC=clang
AR=ar
AR_FLAGS=r
LOCAL_CFLAGS=-I.

%.o: %.c
	$(CC) $(CFLAGS) $(LOCAL_CFLAGS) -c $< -o $@

all: libsomething.a something_prog1_main

LIBSTARCH_OBJS = libsomething/foo.o libsomething/bar.o libsomething/common.o
LIBSTARCH_HEADERS = libsomething/bar.h libsomething/foo.h libsomething/common.h

libsomething.a: $(LIBSTARCH_OBJS)
	$(AR) $(AR_FLAGS) $@ $^

STARCH_PROG1_MAIN_OBJS = programs/something_prog1/something_prog1_main.o

something_prog1_main: $(STARCH_PROG1_MAIN_OBJS) libsomething.a
	$(CC) -o $@ $^

clean:
	rm -f $(LIBSTARCH_OBJS) $(STARCH_PROG1_MAIN_OBJS) libsomething.a something_prog1_main

install: something_prog1_main libsomething.a $(LIBSTARCH_HEADERS)
	mkdir -p $(prefix)/bin
	mkdir -p $(prefix)/lib
	mkdir -p $(prefix)/include/libsomething
	install -m 755 something_prog1_main $(prefix)/bin
	install -m 644 libsomething.a $(prefix)/lib
	$(foreach header,$(LIBSTARCH_HEADERS),install -m 644 $(header) $(prefix)/include/libsomething;)
