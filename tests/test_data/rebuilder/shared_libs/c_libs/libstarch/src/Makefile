prefix=/usr/local
#CC=clang
AR=ar
AR_FLAGS=r
LOCAL_CFLAGS=-I. -fPIC

LIBSTARCH_OBJS = libstarch/amylose.o libstarch/amylopectin.o libstarch/common.o
LIBSTARCH_HEADERS = libstarch/amylopectin.h libstarch/amylose.h libstarch/common.h

libstarch.so: $(LIBSTARCH_OBJS)
	$(CC) -shared $(LOCAL_LDFLAGS) $^ -o $@

STARCH_PROG1_MAIN_OBJS = programs/starch_prog1/starch_prog1_main.o
STARCH_PROG1_MAIN_LIBS = -lstarch

starch_prog1_main: $(STARCH_PROG1_MAIN_OBJS) libstarch.so
	$(CC) $(LDFLAGS) $(LOCAL_LDFLAGS) -o $@ $(STARCH_PROG1_MAIN_OBJS) $(STARCH_PROG1_MAIN_LIBS)

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
