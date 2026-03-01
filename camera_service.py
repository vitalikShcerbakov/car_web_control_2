import time

camera_available = False

try:
    import cv2
    from picamera2 import Picamera2

    camera_available = True
except ImportError:
    cv2 = None
    Picamera2 = None
    camera_available = False


class BaseCamera:
    def gen_frames(self):
        """Должен возвращать генератор кадров"""
        raise NotImplementedError


class PiCameraService(BaseCamera):
    def __init__(self):
        self.picam2 = Picamera2()
        self.picam2.configure(
            self.picam2.create_video_configuration(
                main={"size": (320, 240), "format": "RGB888"}
            )
        )
        self.picam2.start()

    def gen_frames(self):
        while True:
            frame = self.picam2.capture_array()
            ret, buffer = cv2.imencode(
                ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60]
            )
            frame = buffer.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )

            time.sleep(0.07)  # ~14 FPS


class DummyCameraService(BaseCamera):
    def gen_frames(self):
        """Заглушка для ПК — отдаёт пустой поток"""
        while True:
            yield (
                b"--frame\r\n"
                b"Content-Type: text/plain\r\n\r\n"
                b"No camera available\r\n"
            )
            time.sleep(1)
