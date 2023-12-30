include $(CURDIR)/../../../../make/mmd.mak

all: keyval.mmd keyval.svg _test_keyval_lexer.py

clean:
	rm -f keyval.mmd keyval.svg _test_keyval_lexer.py

_test_keyval_lexer.py: keyval.btl Makefile
	@$(_MMD_BEST_BIN) btl make_code $< _test keyval $@
