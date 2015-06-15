BUILDDIR = build

.PHONY: docs tests clean help

docs:
	sphinx-build -b html docs $(BUILDDIR)/html

tests:
	py.test-3

clean:
	rm -rf $(BUILDDIR)/*

help:
	@echo "usage: make [target]"
	@echo
	@echo "targets:"
	@echo "  docs   to build html documentation with sphinx"
	@echo "  clean  to clean the build directory"
	@echo "  help   to display this help message"
