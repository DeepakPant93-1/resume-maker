# Forwards every target to the repo-root Makefile, so `make <target>` works from this folder too.
.DEFAULT_GOAL := help

.DEFAULT help:
	@$(MAKE) --no-print-directory -C ../.. $@
