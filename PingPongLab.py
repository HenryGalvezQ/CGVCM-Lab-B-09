import cv2
import numpy as np
import socket
import argparse

parser = argparse.ArgumentParser(description="Track two colors and send Y positions")
parser.add_argument('--ip', default='127.0.0.1', help='IP of Unity host')
parser.add_argument('--port', type=int, default=5065, help='UDP port')
parser.add_argument('--camera', type=int, default=0, help='Camera index')
args = parser.parse_args()

UDP_IP   = args.ip
UDP_PORT = args.port
sock     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)   # ó tu fuente
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# HSV ranges (ajusta con trackbars si lo deseas)
red_lower1  = np.array([ 0,120, 70]); red_upper1  = np.array([10,255,255])
red_lower2  = np.array([170,120,70]); red_upper2  = np.array([180,255,255])
blue_lower  = np.array([100,150, 50]); blue_upper  = np.array([140,255,255])

def get_centroid(mask):
    cnts,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts: return None
    c = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(c) < 300: return None
    M = cv2.moments(c)
    return int(M['m10']/M['m00']), int(M['m01']/M['m00'])

while True:
    ret, frame = cap.read()
    if not ret: break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- rojo (dos rangos por 0/180) ---
    maskR = cv2.inRange(hsv, red_lower1, red_upper1) | cv2.inRange(hsv, red_lower2, red_upper2)
    # --- azul ---
    maskB = cv2.inRange(hsv, blue_lower , blue_upper)

    maskR = cv2.erode(maskR, None, iterations=2)
    maskR = cv2.dilate(maskR, None, iterations=2)
    maskB = cv2.erode(maskB, None, iterations=2)
    maskB = cv2.dilate(maskB, None, iterations=2)

    posR = get_centroid(maskR)
    posB = get_centroid(maskB)

    if posR: cv2.circle(frame, posR, 8, (0,0,255), -1)
    if posB: cv2.circle(frame, posB, 8, (255,0,0), -1)

    # Enviar sólo si detecta ambos
    if posR and posB:
        # Sólo Y, manda como "yLeft,yRight"
        message = f"{posB[1]},{posR[1]}".encode('utf-8')
        sock.sendto(message, (UDP_IP, UDP_PORT))

    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1) == 27: break          # Esc para salir

cap.release()
cv2.destroyAllWindows()
