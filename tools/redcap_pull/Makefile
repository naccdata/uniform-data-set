PREFIX ?= ~
VERSION = "1.2.1"

all: install

install:
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	install -m 0755 rcpull-wrapper $(DESTDIR)$(PREFIX)/bin/rcpull

uninstall:
	@$(RM) $(DESTDIR)$(PREFIX)/bin/rcpull
	@docker rmi naccdata/rcpull:$(VERSION)
	@docker rmi naccdata/rcpull:latest

build:
	@docker build -t naccdata/rcpull:$(VERSION) . \
	&& docker tag naccdata/rcpull:$(VERSION) naccdata/rcpull:latest

.PHONY: all install uninstall build
