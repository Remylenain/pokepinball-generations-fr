.PHONY: all tools clean tidy patch

.SUFFIXES:
.SECONDEXPANSION:
.PRECIOUS:
.SECONDARY:

ROM := PinballGenerations.gbc
OBJS := main.o wram.o sram.o

# Patch IPS : ROM de base officielle (sha1 9402014d14969432142abfde728c6f1a10ee4dac)
BASEROM ?= Pokemon Pinball US.gbc
PATCH   ?= PinballGenerations-1.6-FR.ips
PYTHON  ?= python

ifeq (,$(shell which sha1sum))
SHA1 := shasum
else
SHA1 := sha1sum
endif

RGBDS ?=
RGBASM  ?= $(RGBDS)rgbasm
RGBLINK ?= $(RGBDS)rgblink
RGBFIX  ?= $(RGBDS)rgbfix
RGBGFX  ?= $(RGBDS)rgbgfx

RGBASMFLAGS  ?=
RGBLINKFLAGS ?=
RGBFIXFLAGS  ?=
RGBGFXFLAGS  ?=

all: $(ROM)

ifeq (,$(filter tools clean tidy,$(MAKECMDGOALS)))
Makefile: tools
endif

%.o: dep = $(shell tools/scan_includes $(@D)/$*.asm)
%.o: %.asm $$(dep)
	$(RGBASM) $(RGBASMFLAGS) -o $@ $<

$(ROM): RGBLINKFLAGS += -l contents/contents.link -n $(ROM:.gbc=.sym) -m $(ROM:.gbc=.map)
$(ROM): RGBFIXFLAGS += -jsvc -k 01 -l 0x33 -m 0x1e -p 0 -r 02 -t "POKEPINBALL" -i VPHE
$(ROM): $(OBJS) contents/contents.link
	$(RGBLINK) $(RGBLINKFLAGS) -o $@ $(OBJS)
	$(RGBFIX) $(RGBFIXFLAGS) $@

patch: $(ROM)
	$(PYTHON) tools/ips.py create "$(BASEROM)" $(ROM) "$(PATCH)"
	$(PYTHON) tools/ips.py verify "$(BASEROM)" "$(PATCH)" $(ROM)

tools:
	$(MAKE) -C tools

tidy:
	rm -f $(ROM) $(OBJS) $(ROM:.gbc=.sym) $(ROM:.gbc=.map)
	$(MAKE) -C tools clean

clean: tidy
	find . \( -iname '*.1bpp' -o -iname '*.2bpp' -o -iname '*.pcm' \) -exec rm {} +

%.interleave.2bpp: %.interleave.png
	$(RGBGFX) $(RGBGFXFLAGS) -o $@ $<
	tools/gfx --interleave --png $< -o $@ $@

%.2bpp: %.png
	$(RGBGFX) $(RGBGFXFLAGS) -o $@ $<

%.1bpp: %.png
	$(RGBGFX) $(RGBGFXFLAGS) -d1 -o $@ $<

%.pcm: %.wav
	tools/pcm -o $@ $<
