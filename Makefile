IMAGE := gest-calc
CAM ?= /dev/video0

build:
	docker build -t $(IMAGE) .

camtest:
	xhost +SI:localuser:root
	docker run -it \
		-e DISPLAY=$(DISPLAY) \
		-e QT_X11_NO_MITSHM=1 \
		-v ./:/opt/project \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		--device $(CAM):/dev/video0 \
		--rm \
		$(IMAGE) python /opt/project/src/gest-calc/webcam_test.py


run:
	xhost +SI:localuser:root
	docker run -it \
		-e DISPLAY=$(DISPLAY) \
		-e QT_X11_NO_MITSHM=1 \
		-v ./:/opt/project \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		--device $(CAM):/dev/video0 \
		--rm \
		$(IMAGE) python /opt/project/src/gest-calc/main.py


test:
	docker run --rm \
		-e PYTHONPATH=/opt/project/src/gest-calc \
		-v ./:/opt/project \
		$(IMAGE) python -m unittest discover -s /opt/project/src/gest-calc/tests -p 'test_*.py' -v


shell:
	xhost +SI:localuser:root
	docker run -it \
		-e DISPLAY=$(DISPLAY) \
		-e QT_X11_NO_MITSHM=1 \
		-v ./:/opt/project \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		--device $(CAM):/dev/video0 \
		--rm \
		$(IMAGE) /bin/bash
