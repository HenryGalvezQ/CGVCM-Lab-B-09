import cv2
import numpy as np
import socket
import argparse
import logging
import json
import threading
import time
from pathlib import Path
from typing import Optional, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track colored objects and send Y-coordinates via UDP.")
    parser.add_argument("--ip", default="127.0.0.1", help="Destination UDP IP address")
    parser.add_argument("--port", type=int, default=5065, help="Destination UDP port")
    parser.add_argument("--camera", type=int, default=0, help="Camera index for cv2.VideoCapture")
    parser.add_argument("--min-area", type=int, default=300, help="Minimum contour area to consider")
    parser.add_argument("--delta", type=int, default=5, help="Minimum Y-change to trigger UDP send")
    parser.add_argument("--calibrate", action="store_true", help="Enable HSV range calibration window")
    parser.add_argument("--config", type=Path, help="Path to save/load HSV config (JSON)")
    return parser.parse_args()


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_hsv_config(path: Path) -> dict:
    if path and path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            logging.warning(f"Failed to parse HSV config at {path}")
    return {}


def save_hsv_config(path: Path, cfg: dict) -> None:
    try:
        path.write_text(json.dumps(cfg, indent=2))
        logging.info(f"Saved HSV config to {path}")
    except Exception as e:
        logging.error(f"Could not save HSV config: {e}")


def create_trackbars(window: str, defaults: dict) -> None:
    cv2.namedWindow(window)
    for name, val in defaults.items():
        cv2.createTrackbar(name, window, val, 255, lambda x: None)


def read_trackbars(window: str) -> dict:
    vals = {}
    for name in ["LH","LS","LV","UH","US","UV"]:
        vals[name] = cv2.getTrackbarPos(name, window)
    return vals


def get_centroid(mask: np.ndarray, min_area: int) -> Optional[Tuple[int, int]]:
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    c = max(cnts, key=cv2.contourArea)
    area = cv2.contourArea(c)
    if area < min_area:
        return None
    M = cv2.moments(c)
    if M["m00"] <= 0:
        return None
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return cx, cy


def process_frame(frame: np.ndarray,
                  hsv_ranges: dict,
                  min_area: int) -> Tuple[Optional[Tuple[int,int]], Optional[Tuple[int,int]], np.ndarray]:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create masks
    maskR1 = cv2.inRange(hsv, np.array(hsv_ranges['red_lower1']), np.array(hsv_ranges['red_upper1']))
    maskR2 = cv2.inRange(hsv, np.array(hsv_ranges['red_lower2']), np.array(hsv_ranges['red_upper2']))
    maskR = maskR1 | maskR2
    maskB = cv2.inRange(hsv, np.array(hsv_ranges['blue_lower']),  np.array(hsv_ranges['blue_upper']))

    # Clean masks
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    maskR = cv2.morphologyEx(maskR, cv2.MORPH_OPEN, kernel, iterations=2)
    maskR = cv2.morphologyEx(maskR, cv2.MORPH_CLOSE, kernel, iterations=2)
    maskB = cv2.morphologyEx(maskB, cv2.MORPH_OPEN, kernel, iterations=2)
    maskB = cv2.morphologyEx(maskB, cv2.MORPH_CLOSE, kernel, iterations=2)

    posR = get_centroid(maskR, min_area)
    posB = get_centroid(maskB, min_area)
    return posR, posB, hsv


def send_positions(sock: socket.socket,
                   addr: Tuple[str,int],
                   posR: Tuple[int,int],
                   posB: Tuple[int,int],
                   prev: dict,
                   delta: int) -> None:
    yR, yB = posR[1], posB[1]
    if abs(yR - prev['yR']) > delta or abs(yB - prev['yB']) > delta:
        msg = f"{yB},{yR}".encode('utf-8')
        sock.sendto(msg, addr)
        prev['yR'], prev['yB'] = yR, yB
        logging.debug(f"Sent UDP message: {msg}")


def main():
    args = parse_args()
    setup_logging()

    # Load or default HSV
    cfg = load_hsv_config(args.config) if args.config else {}
    hsv_ranges = cfg.get('hsv_ranges', {
        'red_lower1': [0,120,70],    'red_upper1': [10,255,255],
        'red_lower2': [170,120,70],  'red_upper2': [180,255,255],
        'blue_lower':  [100,150,50],  'blue_upper':  [140,255,255],
    })

    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not cap.isOpened():
        logging.error(f"Cannot open camera index {args.camera}")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (args.ip, args.port)
    prev_pos = {'yR': 0, 'yB': 0}

    if args.calibrate and args.config:
        win = 'Calibration'
        create_trackbars(win, {
            'LH': hsv_ranges['red_lower1'][0], 'LS': hsv_ranges['red_lower1'][1], 'LV': hsv_ranges['red_lower1'][2],
            'UH': hsv_ranges['red_upper2'][0], 'US': hsv_ranges['red_upper2'][1], 'UV': hsv_ranges['red_upper2'][2],
        })

    try:
        while True:
            start = cv2.getTickCount()
            ret, frame = cap.read()
            if not ret:
                logging.warning("Frame grab failed, exiting")
                break

            if args.calibrate and args.config:
                vals = read_trackbars(win)
                # Example: update only red lower hue for demo
                hsv_ranges['red_lower1'][0] = vals['LH']
                # ...adjust other ranges similarly...

            posR, posB, hsv = process_frame(frame, hsv_ranges, args.min_area)

            # Draw
            if posR:
                cv2.circle(frame, posR, 8, (0,0,255), -1)
            if posB:
                cv2.circle(frame, posB, 8, (255,0,0), -1)

            if posR and posB:
                send_positions(sock, dest, posR, posB, prev_pos, args.delta)

            # Compute FPS
            dt = (cv2.getTickCount() - start)/cv2.getTickFrequency()
            fps = 1.0 / dt if dt>0 else 0
            cv2.putText(frame, f"FPS: {fps:.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            cv2.imshow("Tracking", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        sock.close()
        # Save config
        if args.config:
            save_hsv_config(args.config, {'hsv_ranges': hsv_ranges})


if __name__ == "__main__":
    main()
