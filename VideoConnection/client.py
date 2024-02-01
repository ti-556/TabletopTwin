import cv2
import socket
import pickle
import struct
import pyaudio
import threading

# Set up the video socket
video_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = "127.0.0.1"  # Change this to the IP address of the server
video_port = 9999

video_client_socket.connect((host_ip, video_port))

# Set up the audio socket
audio_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
audio_port = 9998

audio_client_socket.connect((host_ip, audio_port))

# Function to send video frames and audio data over TCP
def send_data(frame):
    # Serialize the frame
    frame_data = pickle.dumps(frame)
    video_msg_size = struct.pack("L", len(frame_data))

    # Send the size of the serialized frame and audio data
    video_client_socket.sendall(video_msg_size)

    # Send the serialized frame
    video_client_socket.sendall(frame_data)

    # Capture audio data
    audio_data = audio_client_socket.recv(1024)

    return audio_data

def audio_client():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100, output=True)

    try:
        while True:
            audio_data = audio_client_socket.recv(2048)  # Adjusted buffer size
            stream.write(audio_data)
    except (socket.error, BrokenPipeError):
        pass
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        audio_client_socket.close()
    
# Open the webcam
cap = cv2.VideoCapture(0)

# Create a thread for the audio client
audio_thread = threading.Thread(target=audio_client)
audio_thread.start()

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # Resize the frame if needed
    # frame = cv2.resize(frame, (640, 480))

    # Send the frame and receive audio data
    audio_data = send_data(frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Wait for the audio thread to finish before releasing resources
audio_thread.join()

# Release resources
cap.release()
video_client_socket.close()
audio_client_socket.close()
cv2.destroyAllWindows()
