run: build
	docker run --rm --publish 8000:8000 --name django_frontend tonic:0.0
build:
	docker build --tag tonic:0.0 .
rm:
	docker container rm django_frontend
