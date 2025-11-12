
# server.py
import cv2, socket, pickle, struct, time, pyaudio, numpy as np

# Config
VIDEO_WIDTH, VIDEO_HEIGHT = 480, 320
JPEG_QUALITY = 50
SERVER_IP = "0.0.0.0"
SERVER_PORT = 9999
RATE = 16000           # audio sample rate (lower = more stable)
CHUNK = 1024           # audio frames per packet
AUDIO_THRESHOLD = 500  # mean abs threshold for noise gate

def make_packet(t: bytes, payload: bytes):
    return t + struct.pack("Q", len(payload)) + payload

print("✅ Server starting...")

# UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
sock.bind((SERVER_IP, SERVER_PORT))

clients = []
print("Waiting for client handshake...")
# wait for one client hello
while True:
    data, addr = sock.recvfrom(1024)
    if addr not in clients:
        clients.append(addr)
        print("✅ Connected:", addr)
    break

# Video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
if not cap.isOpened():
    raise SystemExit("Camera not found")

# Audio capture
pa = pyaudio.PyAudio()
audio_stream = pa.open(format=pyaudio.paInt16,
                       channels=1,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)

print("🎥 Streaming started (video + audio)... Press Ctrl+C to stop")

try:
    while True:
        # === Video ===
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.resize(frame, (VIDEO_WIDTH, VIDEO_HEIGHT))
        _, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        v_payload = pickle.dumps(jpg)

        v_packet = make_packet(b'V', v_payload)

        # send video packet
        for c in clients:
            try:
                sock.sendto(v_packet, c)
            except Exception as e:
                print("Video send err:", e)

        # === Audio ===
        try:
            raw = audio_stream.read(CHUNK, exception_on_overflow=False)
            arr = np.frombuffer(raw, dtype=np.int16)
            # simple noise gate
            if np.abs(arr).mean() > AUDIO_THRESHOLD:
                # normalize a little to avoid clipping
                peak = max(1, np.max(np.abs(arr)))
                factor = 15000 / peak
                arr = (arr * factor).astype(np.int16)
                a_payload = arr.tobytes()
                a_packet = make_packet(b'A', a_payload)
                for c in clients:
                    try:
                        sock.sendto(a_packet, c)
                    except Exception:
                        pass
            # else: skip sending silence
        except Exception as e:
            # ignore intermittent audio read issues
            pass

        time.sleep(0.02)  # small delay to avoid flooding

except KeyboardInterrupt:
    print("Stopping server...")

finally:
    cap.release()
    audio_stream.stop_stream()
    audio_stream.close()
    pa.terminate()
    sock.close()
