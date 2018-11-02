#TAG:=$(shell date +%y.%m.%d)
TAG:=$(shell date +%y.%m.%d)
SHELL := /bin/bash
TIME:=$(shell date +%H%M%S)
PROJECT:=autocut
PROJECT_DOCKER_FILE:=$(PROJECT).Dockerfile
PROJECT_DOCKER_FILE_PRODUCTION:=$(PROJECT).prod.Dockerfile
COMMON=~/ws/common
BUILD:=$(shell pwd)/build
SRC=$(pwd)../src
REPOSITORY=$(shell echo $(PROJECT):$(TAG) | tr '[:upper:]' '[:lower:]')

TAG_PROD=prod/$(REPOSITORY)
TAG_DEV=dev/$(REPOSITORY)

LAST_IMAGE_PROD=$(BUILD)/last_image_prod
LAST_IMAGE_DEV=$(BUILD)/last_image_dev

TAG_PREV_PROD=$(shell cat $(LAST_IMAGE_PROD))
TAG_PREV_DEV=$(shell cat $(LAST_IMAGE_DEV))

.PHONY: all preliminary clean dev prod clean_prod clean_dev
all: prod dev

$(BUILD):
	mkdir -p $(BUILD)

preliminary: $(COMMON)/entrypoint.sh $(COMMON)/bashrc $(BUILD)
	cp $(COMMON)/entrypoint.sh $(BUILD)/entrypoint.sh
	cp $(COMMON)/bashrc $(BUILD)/bashrc

$(BUILD)/autocut.py: $(SRC)/autocut.py
	cp  $(SRC)/autocut.py $(BUILD)/autocut.py

prod: $(PROJECT_DOCKER_FILE_PRODUCTION) preliminary $(BUILD)/autocut.py clean_prod
	docker build --tag $(TAG_PROD) --file $(PROJECT_DOCKER_FILE_PRODUCTION) .
	echo $(TAG_PROD) > $(LAST_IMAGE_PROD)

dev: $(PROJECT_DOCKER_FILE) preliminary prod clean_dev
	docker build --build-arg DATE=$(TAG) --tag $(TAG_DEV) --file $(PROJECT_DOCKER_FILE) .
	echo $(TAG_DEV) > $(LAST_IMAGE_DEV)

clean_prod: $(BUILD) clean_dev
	if [[ "$(TAG_PREV_PROD)" != "" && "$(TAG_PREV_PROD)" != "$(TAG)" ]] ; \
	then \
	    docker rmi $(TAG_PREV_PROD); \
	fi;

clean_dev: $(BUILD)
	if [[ "$(TAG_PREV_DEV)" != "" && "$(TAG_PREV_DEV)" != "$(TAG)" ]] ; \
	then \
	    docker rmi $(TAG_PREV_DEV); \
	fi;

clean:
	rm -rf $(BUILD)
