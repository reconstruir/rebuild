include $(_TEST_MAKE_DIR)/common.mk

ifdef REBUILD_NO_PROGRAMS
	programs=
else
	programs=starch_prog1_main
endif

all: libstarch.a $(programs)

LIBSTARCH_OBJS = libstarch/amylose.o libstarch/amylopectin.o libstarch/common.o
LIBSTARCH_HEADERS = libstarch/amylopectin.h libstarch/amylose.h libstarch/common.h

libstarch.a: $(LIBSTARCH_OBJS)
	$(AR) $(AR_FLAGS) $@ $^

STARCH_PROG1_MAIN_OBJS = programs/starch_prog1/starch_prog1_main.o

starch_prog1_main: $(STARCH_PROG1_MAIN_OBJS) libstarch.a
	$(CC) $(CFLAGS) $(LOCAL_CFLAGS) -o $@ $^

clean:
	rm -f $(LIBSTARCH_OBJS) $(STARCH_PROG1_MAIN_OBJS) libstarch.a $(programs)

install: $(programs) libstarch.a $(LIBSTARCH_HEADERS)
	mkdir -p $(prefix)/bin
	mkdir -p $(prefix)/lib
	mkdir -p $(prefix)/include/libstarch
ifneq ($(REBUILD_NO_PROGRAMS),)
	install -m 755 $(programs) $(prefix)/bin
endif
	install -m 644 libstarch.a $(prefix)/lib
	$(foreach header,$(LIBSTARCH_HEADERS),install -m 644 $(header) $(prefix)/include/libstarch;)
