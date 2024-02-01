import cv2
import socket
import struct
import pickle
import pyaudio
import threading

class VideoClient:
    def __init__(self, ip, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))

        self.cap = cv2.VideoCapture(0)
        self.audio_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=1024)

    def video_stream(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            data = pickle.dumps(frame)
            message = struct.pack("Q", len(data)) + data
            self.client_socket.sendall(message)

            cv2.imshow('SENDING VIDEO', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.client_socket.close()
                break

    def audio_stream(self):
        while True:
            data = self.client_socket.recv(1024)
            self.audio_stream.write(data)

    def start(self):
        thread_video = threading.Thread(target=self.video_stream)
        thread_audio = threading.Thread(target=self.audio_stream)
        thread_video.start()
        thread_audio.start()
        thread_video.join()
        thread_audio.join()

if __name__ == "__main__":
    video_client = VideoClient(ip='127.0.0.1', port=8485)
    video_client.start()
