docker-run:
	docker run -p 8000:8000 --gpus all -it --rm face-rec-nvidia:latest

docker-build:
	docker build -t face-rec-nvidia:latest .

.ONESHELL:
test:
	cd test/
	python -B -m pytest -s -p no:cacheprovider