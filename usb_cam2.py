import cv2
import sys
from flask import Flask, Response, render_template
import threading
import time

app = Flask(__name__)
window_name = "Webcam"
hq_frame = None
lq_frame = None
mq_frame = None
lock = threading.Lock()

def saveFrame(device):
    global hq_frame, mq_frame, lq_frame
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        print(f"No se puede abrir el dispositivo de video {device}")
        sys.exit(1)

    cv2.namedWindow(window_name)

    while True:
        lock.acquire() # Get lock
        
        ret, hq_frame = cap.read()
        if not ret:
            print("No se puede recibir el frame (stream end?). Saliendo ...")
            lock.release() # Release lock
            break

        cv2.imshow(window_name, hq_frame)

        mq_scale = 0.5
        lq_scale = 0.25

        mq_frame = cv2.resize(hq_frame, (int(hq_frame.shape[1] * mq_scale), int(hq_frame.shape[0] * mq_scale)))
        lq_frame = cv2.resize(hq_frame, (int(hq_frame.shape[1] * lq_scale), int(hq_frame.shape[0] * lq_scale)))

        lock.release() # Release lock

        if cv2.waitKey(1) == 27:  # Presiona 'ESC' para salir
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
    if len(sys.argv) < 2:
        print("Usage: python3 usb_cam.py <video_device>")
        sys.exit(1)

    device = sys.argv[1]

    capture_thread = threading.Thread(target=saveFrame, args=(device,))
    capture_thread.start()

    # Ejecutar la aplicación Flask
    app.run(host='0.0.0.0', port=5000)
