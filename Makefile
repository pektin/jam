BUILDDIR = build

.PHONY: docs tests clean help

docs:
	@sphinx-build -b html docs $(BUILDDIR)/html

tests:
	@py.test-3

clean:
	@rm -rf $(BUILDDIR)

install:
	@ln -s $(realpath jam) /usr/bin/jam

help:
	@echo "usage: make [target]"
	@echo
	@echo "targets:"
	@echo "  docs      to build html documentation with sphinx"
	@echo "  tests     to run the tests (or just use py.test-3)"
	@echo "  clean     to clean the build directory"
	@echo "  install   to install the jam compiler tool (symlinks)"
	@echo "  help      to display this help message"
