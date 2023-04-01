.ONESHELL:
test:
	cd test/
	python -B -m pytest -p no:cacheprovider

.PHONY: test