.ONESHELL:
test:
	cd test/
	SET PYTHONDONTWRITEBYTECODE=1
	python -B -m pytest -p no:cacheprovider

.PHONY: test