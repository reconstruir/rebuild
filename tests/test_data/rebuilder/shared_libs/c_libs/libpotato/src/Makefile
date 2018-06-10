prefix=/usr/local
CC=clang
AR=ar
AR_FLAGS=r
LOCAL_CFLAGS=-I. -fPIC
LOCAL_LDFLAGS=-L.

%.o: %.c
	$(CC) $(CFLAGS) $(LOCAL_CFLAGS) -c $< -o $@

all: libpotato.so potato_prog1_main

LIBPOTATO_OBJS = libpotato/potato.o libpotato/common.o
LIBPOTATO_HEADERS = libpotato/potato.h libpotato/common.h

libpotato.so: $(LIBPOTATO_OBJS)
	$(CC) -shared $(LOCAL_LDFLAGS) $^ -o $@

POTATO_PROG1_MAIN_OBJS = programs/potato_prog1/potato_prog1_main.o
POTATO_PROG1_MAIN_LIBS = -lpotato -lstarch

potato_prog1_main: $(POTATO_PROG1_MAIN_OBJS) libpotato.so
	$(CC) $(LDFLAGS) $(LOCAL_LDFLAGS) -o $@ $(POTATO_PROG1_MAIN_OBJS) $(POTATO_PROG1_MAIN_LIBS)

clean:
	rm -f $(LIBPOTATO_OBJS) $(POTATO_PROG1_MAIN_OBJS) libpotato.so potato_prog1_main

install: potato_prog1_main libpotato.so $(LIBPOTATO_HEADERS)
	mkdir -p $(prefix)/bin
	mkdir -p $(prefix)/lib
	mkdir -p $(prefix)/include/libpotato
	install -m 755 potato_prog1_main $(prefix)/bin
	install -m 644 libpotato.so $(prefix)/lib
	$(foreach header,$(LIBPOTATO_HEADERS),install -m 644 $(header) $(prefix)/include/libpotato;)
