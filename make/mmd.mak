_BES_ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
_MMD_BEST_BIN=$(realpath $(_BES_ROOT_DIR)/../bin/best.sh)

%.svg: %.btl Makefile
	@$(_MMD_BEST_BIN) btl make_diagram --format svg $< $@

%.jpg: %.btl Makefile
	@$(_MMD_BEST_BIN) btl make_diagram --format jpg $< $@

%.mmd: %.btl Makefile
	@$(_MMD_BEST_BIN) btl make_mmd $< $@
