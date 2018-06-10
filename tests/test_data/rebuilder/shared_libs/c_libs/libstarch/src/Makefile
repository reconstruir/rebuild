prefix=/usr/local
#CC=clang
AR=ar
AR_FLAGS=r
LOCAL_CFLAGS=-I.
LOCAL_LDFLAGS=

%.o: %.c
	$(CC) $(CFLAGS) $(LOCAL_CFLAGS) -c $< -o $@

ifdef REBUILD_NO_PROGRAMS
	programs=
else
	programs=starch_prog1_main
endif

all: libstarch.so $(programs)

LIBSTARCH_OBJS = libstarch/amylose.o libstarch/amylopectin.o libstarch/common.o
LIBSTARCH_HEADERS = libstarch/amylopectin.h libstarch/amylose.h libstarch/common.h

libstarch.a: $(LIBSTARCH_OBJS)
	$(AR) $(AR_FLAGS) $@ $^

libstarch.so: libstarch.a
	$(CC) -shared $(LOCAL_LDFLAGS) $@ -o $^

STARCH_PROG1_MAIN_OBJS = programs/starch_prog1/starch_prog1_main.o

starch_prog1_main: $(STARCH_PROG1_MAIN_OBJS) libstarch.so
	$(CC) $(CFLAGS) $(LOCAL_CFLAGS) -o $@ $^

clean:
	rm -f $(LIBSTARCH_OBJS) $(STARCH_PROG1_MAIN_OBJS) libstarch.so $(programs)

install: $(programs) libstarch.so $(LIBSTARCH_HEADERS)
	mkdir -p $(prefix)/bin
	mkdir -p $(prefix)/lib
	mkdir -p $(prefix)/include/libstarch
ifneq ($(REBUILD_NO_PROGRAMS),)
	install -m 755 $(programs) $(prefix)/bin
endif
	install -m 644 libstarch.so $(prefix)/lib
	$(foreach header,$(LIBSTARCH_HEADERS),install -m 644 $(header) $(prefix)/include/libstarch;)
