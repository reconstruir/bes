include $(CURDIR)/../../../../make/mmd.mak

all: _test_keyval1_lexer.mmd _test_keyval1_lexer.svg _test_keyval1_lexer.py

clean:
	rm -f _test_keyval1_lexer.mmd _test_keyval1_lexer.svg _test_keyval1_lexer.py

_test_keyval1_lexer.py: _test_keyval1_lexer.btl Makefile
	@$(_MMD_BEST_BIN) btl make_code $< _test keyval1_lexer $@
