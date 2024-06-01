# webcam_webserver
Simple webcam server to play video remotely

## How to use
1. First install dependencies  
`chmod +x install.sh && ./install.sh`
2. Run this in one computer (**A**) with (use your video device):  
`python3 usb_cam.py /dev/video0`
3. Open your browser in a different remote PC (in the same net) and search:
`http://ip_of_A:5000`  
You can see your computer A ip with `ifconfig` in Linux and `ipconfig` in Windows. In normal house should be 192.168.0.something or 192.168.1.something
