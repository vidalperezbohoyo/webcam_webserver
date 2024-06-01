import cv2
import sys

window_name = "Webcam"
status = "Open"

def minimize_window(event, x, y, flags, param): 
    global status
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Click")
        
        status = "Closed"
        cv2.destroyWindow(window_name)  # Cierra la ventana
        cv2.namedWindow(window_name)  # Vuelve a crear la ventana
        cv2.setMouseCallback(window_name, minimize_window)  # Reasigna el callback

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 webcam.py <dispositivo_de_video>")
        sys.exit(1)

    device = sys.argv[1]

    # Intenta abrir el dispositivo de video
    cap = cv2.VideoCapture(device)

    if not cap.isOpened():
        print(f"No se puede abrir el dispositivo de video {device}")
        sys.exit(1)


    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, minimize_window)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se puede recibir el frame (stream end?). Saliendo ...")
            break
        
        if (status == "Open"):
                print("Show")
                cv2.imshow(window_name, frame)

        if cv2.waitKey(1) == 27:  # Presiona 'ESC' para salir
            break

    cap.release()
    cv2.destroyAllWindows()



