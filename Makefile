
#build docker container
build:
	docker build -t ucschexmap/compute:dev .

#run the tests in tests/run all
test:
	cd tests && ./run all

#produce a shell from current docker image
shell:
	docker run -it ucschexmap/compute:dev

#run tests/run inside docker container
dtest:
	docker run ucschexmap/compute:dev /bin/bash && make test

#push to the docker store
push:
	docker push ucschexmap/compute:dev
