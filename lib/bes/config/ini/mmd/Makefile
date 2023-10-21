THEME=forest #dark
WIDTH=1280
HEIGHT=1024

all: ini.svg

clean:
	rm -f ini.svg

MMDC_ARGS=--theme ${THEME} --width ${WIDTH} --height ${HEIGHT}
%.svg: %.mmd %.css Makefile
	./node_modules/.bin/mmdc ${MMDC_ARGS} --cssFile $(word 2,$^) --input $< -o $@

