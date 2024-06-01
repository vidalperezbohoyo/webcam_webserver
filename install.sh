#!/bin/sh
sudo apt-get install libopencv-dev
sudo apt-get install libx11-dev

sudo apt install python3-pip

pip install opencv-python
pip install opencv-python flask

sudo ufw allow 5000/tcp
sudo ufw enable

