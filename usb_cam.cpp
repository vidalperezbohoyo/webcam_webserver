#include <opencv2/opencv.hpp>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <iostream>

using namespace cv;

// Prototipo de la función de callback
void onMouse(int event, int x, int y, int flags, void* userdata);

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Uso: " << argv[0] << " <dispositivo de video>" << std::endl;
        return -1;
    }

    // Obtener el nombre del dispositivo de video del primer parámetro
    char* videoDevice = argv[1];

    // Capturar el video del dispositivo especificado
    VideoCapture cap(videoDevice);

    // Verificar si la captura de video se abrió correctamente
    if (!cap.isOpened()) {
        std::cerr << "Error al abrir el dispositivo de video " << videoDevice << std::endl;
        return -1;
    }

    // Crear una ventana
    const char* windowName = "Webcam";
    namedWindow(windowName, WINDOW_AUTOSIZE);

    // Configurar la función de callback para el evento del mouse
    setMouseCallback(windowName, onMouse, (void*)windowName);

    Mat frame;
    while (true) {
        // Capturar un frame
        cap >> frame;
        if (frame.empty()) break;

        // Mostrar el frame
        imshow(windowName, frame);

        // Salir si se presiona la tecla 'q'
        if (waitKey(30) == 'q') break;
    }

    // Liberar el dispositivo de captura de video y cerrar la ventana
    cap.release();
    destroyAllWindows();

    return 0;
}

// Implementación de la función de callback
void onMouse(int event, int x, int y, int flags, void* userdata) {
    if (event == EVENT_LBUTTONDOWN) {
        // Obtener el nombre de la ventana
        const char* windowName = (const char*)userdata;

        // Minimizar la ventana usando X11
        Display* display = XOpenDisplay(NULL);
        if (display) {
            Window root = DefaultRootWindow(display);
            Atom wmState = XInternAtom(display, "_NET_WM_STATE", False);
            Atom wmStateHidden = XInternAtom(display, "_NET_WM_STATE_HIDDEN", False);

            XClientMessageEvent xClientMessageEvent = {0};
            xClientMessageEvent.type = ClientMessage;
            xClientMessageEvent.window = XGetWindowAttributes(display, XRootWindow(display, DefaultScreen(display))).root;
            xClientMessageEvent.message_type = wmState;
            xClientMessageEvent.format = 32;
            xClientMessageEvent.data.l[0] = 1; // _NET_WM_STATE_ADD
            xClientMessageEvent.data.l[1] = wmStateHidden;
            xClientMessageEvent.data.l[2] = 0;
            xClientMessageEvent.data.l[3] = 1;

            XSendEvent(display, root, False, SubstructureNotifyMask, (XEvent*)&xClientMessageEvent);
            XFlush(display);
            XCloseDisplay(display);
        }
    }
}

