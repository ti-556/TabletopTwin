import cv2
import socket
import pickle
import struct
import pyaudio
import threading

# Function to receive video frames over TCP
def receive_video(client_socket):
    data = b""
    payload_size = struct.calcsize("L")

    while True:
        # Receive the size of the serialized frame
        while len(data) < payload_size:
            data += client_socket.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]

        msg_size = struct.unpack("L", packed_msg_size)[0]

        # Receive the serialized frame data
        while len(data) < msg_size:
            data += client_socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Deserialize the frame and display it
        frame = pickle.loads(frame_data)
        cv2.imshow("Server Side", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Function to handle audio streaming
def audio_server(client_socket):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, frames_per_buffer=2048)  # Adjusted parameters

    try:
        while True:
            audio_data = stream.read(2048)  # Adjusted buffer size
            client_socket.sendall(audio_data)
    except (socket.error, BrokenPipeError):
        pass
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    # Set up the video socket
    video_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_host_ip = "0.0.0.0"
    video_port = 9999
    video_server_socket.bind((video_host_ip, video_port))
    video_server_socket.listen(5)

    print(f"Video server listening on {video_host_ip}:{video_port}")

    # Accept a connection from a video client
    video_client_socket, video_addr = video_server_socket.accept()
    print(f"Video connection from {video_addr}")

    # Set up the audio socket
    audio_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    audio_host_ip = "0.0.0.0"
    audio_port = 9998
    audio_server_socket.bind((audio_host_ip, audio_port))
    audio_server_socket.listen(5)

    print(f"Audio server listening on {audio_host_ip}:{audio_port}")

    # Accept a connection from an audio client
    audio_client_socket, audio_addr = audio_server_socket.accept()
    print(f"Audio connection from {audio_addr}")

    # Create separate threads for receiving video and audio
    video_thread = threading.Thread(target=receive_video, args=(video_client_socket,))
    audio_thread = threading.Thread(target=audio_server, args=(audio_client_socket,))

    video_thread.start()
    audio_thread.start()

    video_thread.join()
    audio_thread.join()

    # Release resources
    cv2.destroyAllWindows()
    video_client_socket.close()
    video_server_socket.close()
    audio_client_socket.close()
    audio_server_socket.close()
