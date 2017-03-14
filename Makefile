
build:
	docker build -t dmccoll/tumormap .
test:
	cd tests && run all
