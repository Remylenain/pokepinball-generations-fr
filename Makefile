.PHONY: all tools clean tidy

.SUFFIXES:
.SECONDEXPANSION:
.PRECIOUS:
.SECONDARY:

ROM := PinballGenerations.gbc
OBJS := main.o wram.o sram.o

RGBDS ?= rgbds-0.6.1/

ifeq (,$(shell which sha1sum))
SHA1 := shasum
else
SHA1 := sha1sum
endif

COMPILE_FLAGS :=

all: $(ROM)

ifeq (,$(filter tools clean tidy,$(MAKECMDGOALS)))
Makefile: tools
endif

%.o: dep = $(shell tools/scan_includes $(@D)/$*.asm)
%.o: %.asm $$(dep)
	$(RGBDS)rgbasm $(COMPILE_FLAGS) -h -Wunmapped-char=0 -l -o $@ $<

$(ROM): $(OBJS) contents/contents.link
	$(RGBDS)rgblink -n $(ROM:.gbc=.sym) -m $(ROM:.gbc=.map) -l contents/contents.link -o $@ $(OBJS)
	$(RGBDS)rgbfix -jsvc -k 01 -l 0x33 -m 0x1e -p 0 -r 02 -t "POKEPINBALL" -i VPHE $@

tools:
	$(MAKE) -C tools

tidy:
	rm -f $(ROM) $(OBJS) $(ROM:.gbc=.sym) $(ROM:.gbc=.map)
	$(MAKE) -C tools clean

clean: tidy
	find . \( -iname '*.1bpp' -o -iname '*.2bpp' -o -iname '*.pcm' \) -exec rm {} +

%.interleave.2bpp: %.interleave.png
	$(RGBDS)rgbgfx -o $@ $<
	tools/gfx --interleave --png $< -o $@ $@

%.2bpp: %.png
	$(RGBDS)rgbgfx -o $@ $<

%.1bpp: %.png
	$(RGBDS)rgbgfx -d1 -o $@ $<

%.pcm: %.wav
	tools/pcm -o $@ $<
