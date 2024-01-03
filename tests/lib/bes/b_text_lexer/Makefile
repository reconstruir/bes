include $(CURDIR)/../../../../make/mmd.mak

all: keyval1.mmd keyval1.svg _test_keyval_lexer.py

clean:
	rm -f keyval1.mmd keyval1.svg _test_keyval_lexer.py

_test_keyval_lexer.py: keyval1.btl Makefile
	@$(_MMD_BEST_BIN) btl make_code $< _test keyval $@
