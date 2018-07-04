prefix=/usr/local
CC=clang
AR=ar
AR_FLAGS=r
LOCAL_CFLAGS=-I. -fPIC
LOCAL_LDFLAGS=-L.

%.o: %.c
	$(CC) $(CFLAGS) $(LOCAL_CFLAGS) -c $< -o $@

ifdef REBUILD_NO_PROGRAMS
	programs=
else
	programs=potato_prog1_main
endif

all: libpotato.so $(programs)

LIBPOTATO_OBJS = libpotato/potato.o libpotato/common.o
LIBPOTATO_HEADERS = libpotato/potato.h libpotato/common.h

libpotato.so: $(LIBPOTATO_OBJS)
	$(CC) -shared $(LOCAL_LDFLAGS) $^ -o $@

POTATO_PROG1_MAIN_OBJS = programs/potato_prog1/potato_prog1_main.o
POTATO_PROG1_MAIN_LIBS = -lpotato -lstarch

potato_prog1_main: $(POTATO_PROG1_MAIN_OBJS) libpotato.so
	$(CC) $(LDFLAGS) $(LOCAL_LDFLAGS) -o $@ $(POTATO_PROG1_MAIN_OBJS) $(POTATO_PROG1_MAIN_LIBS)

clean:
	rm -f $(LIBPOTATO_OBJS) $(POTATO_PROG1_MAIN_OBJS) libpotato.so $(programs)

install: $(programs) libpotato.so $(LIBPOTATO_HEADERS)
	mkdir -p $(prefix)/bin
	mkdir -p $(prefix)/lib
	mkdir -p $(prefix)/include/libpotato
ifndef REBUILD_NO_PROGRAMS
	install -m 755 $(programs) $(prefix)/bin
endif
	install -m 644 libpotato.so $(prefix)/lib
	$(foreach header,$(LIBPOTATO_HEADERS),install -m 644 $(header) $(prefix)/include/libpotato;)
