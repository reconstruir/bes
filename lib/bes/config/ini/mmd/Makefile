THEME=forest #dark
WIDTH=2000
HEIGHT=1600

all: ini.svg

clean:
	rm -f ini.svg

MMDC_ARGS=--theme ${THEME} --width ${WIDTH} --height ${HEIGHT}
%.svg: %.mmd %.css Makefile
	./node_modules/.bin/mmdc ${MMDC_ARGS} --cssFile $(word 2,$^) --input $< -o $@

