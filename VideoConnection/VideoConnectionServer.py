import cv2
import socket
import struct
import pickle
import pyaudio
import threading

class VideoServer:
    def __init__(self, ip, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)
        self.client_socket, self.addr = self.server_socket.accept()

        self.data = b""
        self.payload_size = struct.calcsize("Q")

        self.frame = None
        self.is_frame_available = False

        self.audio_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        self.audio_stream.start_stream()

    def video_stream(self):
        while True:
            while len(self.data) < self.payload_size:
                self.data += self.client_socket.recv(4096)
            packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(self.data) < msg_size:
                self.data += self.client_socket.recv(4096)
            frame_data = self.data[:msg_size]
            self.data = self.data[msg_size:]

            self.frame = pickle.loads(frame_data)
            cv2.imshow("RECEIVING VIDEO", self.frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

            self.is_frame_available = True

    def audio_stream(self):
        while True:
            data = self.audio_stream.read(1024)
            self.client_socket.sendall(data)

    def start(self):
        thread_video = threading.Thread(target=self.video_stream)
        thread_audio = threading.Thread(target=self.audio_stream)
        thread_video.start()
        thread_audio.start()
        thread_video.join()
        thread_audio.join()

if __name__ == "__main__":
    video_server = VideoServer(ip='', port=8485)
    video_server.start()
