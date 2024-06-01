import cv2
import sys
from flask import Flask, Response, render_template
import threading
import argparse

app = Flask(__name__)
window_name = "Webcam"

# Last stored frames
hq_frame = None
lq_frame = None
mq_frame = None

lock = threading.Lock()
running = True

def saveFrame(device, imshow):
    global hq_frame, mq_frame, lq_frame

    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        print(f"Unable to open {device}")
        sys.exit(1)

    cv2.namedWindow(window_name)

    while running:
        lock.acquire() # Get lock
        
        ret, hq_frame = cap.read()
        if not ret:
            print("Unable to retrieve frame...")
            lock.release() # Release lock
            break
        
        if (imshow):
            cv2.imshow(window_name, hq_frame)

        mq_scale = 0.5
        lq_scale = 0.25

        mq_frame = cv2.resize(hq_frame, (int(hq_frame.shape[1] * mq_scale), int(hq_frame.shape[0] * mq_scale)))
        lq_frame = cv2.resize(hq_frame, (int(hq_frame.shape[1] * lq_scale), int(hq_frame.shape[0] * lq_scale)))

        lock.release() # Release lock

        if cv2.waitKey(1) == 27: 
            lock.release()
            break

    cap.release()
    cv2.destroyAllWindows()

def readHQ():
    global hq_frame
    while True:
        
        lock.acquire() # Get lock

        if hq_frame is None:
            lock.release() # Release lock
            continue
        
        _, buffer = cv2.imencode('.jpg', hq_frame)

        hq_frame = None
        lock.release() # Release lock

        encoded = buffer.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + encoded + b'\r\n')

def readLQ():
    global lq_frame
    while True:
        
        lock.acquire() # Get lock

        if lq_frame is None:
            lock.release() # Release lock
            continue
        
        _, buffer = cv2.imencode('.jpg', lq_frame)

        lq_frame = None
        lock.release() # Release lock

        encoded = buffer.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + encoded + b'\r\n')

def readMQ():
    global mq_frame
    while True:
        
        lock.acquire() # Get lock

        if mq_frame is None:
            lock.release() # Release lock
            continue
        
        _, buffer = cv2.imencode('.jpg', mq_frame)

        mq_frame = None
        lock.release() # Release lock

        encoded = buffer.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + encoded + b'\r\n')

@app.route('/video_feed_hq')
def video_feed_hq():
    return Response(readHQ(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_mq')
def video_feed_mq():
    return Response(readMQ(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_lq')
def video_feed_lq():
    return Response(readLQ(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')
 
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description='Webcam streaming server')
    parser.add_argument('video_device', type=str, help='Video device index. Example: /dev/video0')
    parser.add_argument('--no-imshow', action='store_true', help='Disable displaying video stream on local pc')
    parser.add_argument('--no-webserver', action='store_true', help='Disable web server')
    args = parser.parse_args()

    imshow = not args.no_imshow
    webserver = not args.no_webserver
    device = args.video_device

    capture_thread = threading.Thread(target=saveFrame, args=(device, imshow, ))
    capture_thread.start()

    if (webserver):
        app.run(host='0.0.0.0', port=5000)
    else:
        # Spin until the user wants to stop
        stdin = None
        while stdin != "q":
            stdin = input("Write: q + [Enter] to close this program:\n")
        
    running = False
    capture_thread.join()
