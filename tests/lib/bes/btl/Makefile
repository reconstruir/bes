DEPTH=../../../..

include $(CURDIR)/$(DEPTH)/make/mmd.mak

TARGETS := \
  _test_keyval_lexer.mmd \
  _test_keyval_lexer.py \
  _test_keyval_lexer.svg \
  _test_simple_lexer.mmd \
  _test_simple_lexer.py \
  _test_simple_lexer.svg \
  _test_simple_parser.mmd \
  _test_simple_parser.py \
  _test_simple_parser.svg \
  $(NULL)

all: $(TARGETS)

clean:
	rm -f $(TARGETS)

touch:
	@touch *.bt*
