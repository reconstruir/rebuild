
$(MAKE_STATIC_LIB): $(MAKE_STATIC_LIB_OBJS)
	$(AR) $(AR_FLAGS) $@ $^