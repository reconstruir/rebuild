prefix=/usr/local
CC=clang
AR=ar
AR_FLAGS=r
LOCAL_CFLAGS=-Isrc

%.o: %.c
	$(CC) $(LOCAL_CFLAGS) -c $< -o $@

all: libstarch.a starch_prog1_main

LIBSTARCH_OBJS = src/libstarch/amylose.o src/libstarch/amylopectin.o src/libstarch/common.o
LIBSTARCH_HEADERS = src/libstarch/amylopectin.h src/libstarch/amylose.h src/libstarch/common.h

libstarch.a: $(LIBSTARCH_OBJS)
	$(AR) $(AR_FLAGS) $@ $^

starch_prog1_main: programs/starch_prog1/starch_prog1_main.o libstarch.a
	$(CC) -o $@ $^

clean:
	rm -f $(LIBSTARCH_OBJS) libstarch.a

install: starch_prog1_main libstarch.a $(LIBSTARCH_HEADERS)
	mkdir -p $(prefix)/bin
	mkdir -p $(prefix)/lib
	mkdir -p $(prefix)/include/libstarch
	install -m 755 starch_prog1_main $(prefix)/bin
	install -m 644 libstarch.a $(prefix)/lib
	$(foreach header,$(LIBSTARCH_HEADERS),install -m 644 $(header) $(prefix)/include/libstarch;)
