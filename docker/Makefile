TAG:=$(shell date +%y.%m.%d)
TIME:=$(shell date +%H%M%S)
PROJECT:=autocut
PROJECT_DOCKER_FILE:=$(PROJECT).Dockerfile
PROJECT_DOCKER_FILE_PRODUCTION:=$(PROJECT).prod.Dockerfile
COMMON=~/ws/common
BUILD:=$(shell pwd)/build
SRC=$(pwd)../src
REPOSITORY=$(shell echo $(PROJECT):$(TAG) | tr '[:upper:]' '[:lower:]')

.PHONY: all dev preliminary clean prod
all: prod dev

$(BUILD):
	mkdir -p $(BUILD)

preliminary: $(COMMON)/entrypoint.sh $(COMMON)/bashrc $(BUILD)
	cp $(COMMON)/entrypoint.sh $(BUILD)/entrypoint.sh
	cp $(COMMON)/bashrc $(BUILD)/bashrc

$(BUILD)/autocut.py: $(SRC)/autocut.py
	cp  $(SRC)/autocut.py $(BUILD)/autocut.py

prod: $(PROJECT_DOCKER_FILE_PRODUCTION) preliminary $(BUILD)/autocut.py
	docker build --tag prod/$(REPOSITORY)  --file $(PROJECT_DOCKER_FILE_PRODUCTION) .

dev: $(PROJECT_DOCKER_FILE) preliminary prod
	docker build --tag local/$(REPOSITORY) --file $(PROJECT_DOCKER_FILE) .

clean:
	rm -rf $(BUILD)
