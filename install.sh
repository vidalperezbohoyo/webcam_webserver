#!/bin/sh
sudo apt-get install libopencv-dev
sudo apt-get install libx11-dev

sudo apt install python3-pip

pip install opencv-python

# g++ -o usb_cam usb_cam.cpp `pkg-config --cflags --libs opencv4` -lX11
# ./usb_cam /dev/video0
pip install opencv-python flask

