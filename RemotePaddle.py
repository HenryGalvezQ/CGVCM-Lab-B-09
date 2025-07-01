import cv2
import numpy as np
import socket
import argparse

# HSV ranges for red and blue markers
RED_LOWER1 = np.array([0, 120, 70])
RED_UPPER1 = np.array([10, 255, 255])
RED_LOWER2 = np.array([170, 120, 70])
RED_UPPER2 = np.array([180, 255, 255])
BLUE_LOWER = np.array([100, 150, 50])
BLUE_UPPER = np.array([140, 255, 255])


def get_centroid(mask):
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    c = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(c) < 300:
        return None
    M = cv2.moments(c)
    return int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])


def main():
    parser = argparse.ArgumentParser(description="Send paddle position over UDP")
    parser.add_argument('--ip', default='127.0.0.1', help='IP of Unity host')
    parser.add_argument('--port', type=int, default=5065, help='UDP port')
    parser.add_argument('--side', choices=['L', 'R'], required=True,
                        help='Paddle side (L or R)')
    parser.add_argument('--color', choices=['red', 'blue'], required=True,
                        help='Color to track')
    parser.add_argument('--camera', type=int, default=0, help='Camera index')
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)

    if args.color == 'red':
        lower1, upper1 = RED_LOWER1, RED_UPPER1
        lower2, upper2 = RED_LOWER2, RED_UPPER2
    else:
        lower1, upper1 = BLUE_LOWER, BLUE_UPPER
        lower2 = upper2 = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, lower1, upper1)
        if lower2 is not None:
            mask |= cv2.inRange(hsv, lower2, upper2)

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        pos = get_centroid(mask)
        if pos:
            message = f"{args.side}:{pos[1]}".encode('utf-8')
            sock.sendto(message, (args.ip, args.port))
            cv2.circle(frame, pos, 8, (0, 255, 0), -1)

        cv2.imshow('Remote Paddle', frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
