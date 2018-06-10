include $(_TEST_MAKE_DIR)/defs.mk

# Common makefile rules for tests that build c/c++ code
%.o: %.c
	$(CC) $(CFLAGS) $(LOCAL_CFLAGS) -c $< -o $@
