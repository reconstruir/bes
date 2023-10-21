

all: ini.svg

clean:
	rm -f ini.svg

%.svg: %.mmd
	./node_modules/.bin/mmdc -i $< -o $@
