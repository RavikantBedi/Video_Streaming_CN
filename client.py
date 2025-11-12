# client.py
import socket, cv2, pickle, struct, time, pyaudio, wave, os
import numpy as np

# Config (must match server audio settings)
RATE = 16000
CHUNK = 1024
OUTPUT_VIDEO_FPS = 20.0
VIDEO_CODEC = "XVID"   # cross-platform common codec
OUT_VIDEO_FILE = f"recorded_{int(time.time())}.avi"
OUT_AUDIO_FILE = f"audio_{int(time.time())}.wav"

# Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)

server_ip = input("Enter Server IP: ")
server_port = 9999
sock.sendto(b"hello", (server_ip, server_port))
print("Handshake sent -> waiting for stream...")

# Audio playback
pa = pyaudio.PyAudio()
audio_stream = pa.open(format=pyaudio.paInt16,
                       channels=1,
                       rate=RATE,
                       output=True,
                       frames_per_buffer=CHUNK)

# Prepare recording objects
fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
video_writer = None  # will initialize after first frame size known
audio_frames = []

# Stats
last_stats_time = time.time()
bytes_recv_in_sec = 0
frame_count = 0
frames_received = 0
lost_packets = 0


cv2.namedWindow("Live Stream", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Live Stream", 1000, 600)  # 👈 Change window size here (width, height)
cv2.moveWindow("Live Stream", 100, 50)
cv2.setWindowProperty("Live Stream", cv2.WND_PROP_TOPMOST, 1)



print("Receiving... Press ESC to stop and save recordings.")

try:
    while True:
        pkt, _ = sock.recvfrom(65536)
        if len(pkt) < 9:
            continue
        pkt_type = pkt[0:1]
        size = struct.unpack("Q", pkt[1:9])[0]
        payload = pkt[9:]

        # sometimes UDP can give truncated payload - ignore if mismatch
        if len(payload) != size:
            # If truncated, skip (count as lost)
            lost_packets += 1
            continue

        bytes_recv_in_sec += len(pkt)

        if pkt_type == b'V':
            # video: payload is pickled jpg bytes
            frames_received += 1
            frame_count += 1
            jpg = pickle.loads(payload)
            img = cv2.imdecode(jpg, cv2.IMREAD_COLOR)
            if img is None:
                continue

            # Initialize video writer when we have frame size
            if video_writer is None:
                h, w = img.shape[:2]
                video_writer = cv2.VideoWriter(OUT_VIDEO_FILE, fourcc, OUTPUT_VIDEO_FPS, (w, h))

            # Draw stats overlay
            now = time.time()
            elapsed = now - last_stats_time
            if elapsed >= 1.0:
                fps = frame_count / elapsed
                bw_kb = bytes_recv_in_sec / 1024.0
                pl = (lost_packets / max(1, frame_count + lost_packets)) * 100
                # reset counters per second
                last_stats_time = now
                frame_count = 0
                bytes_recv_in_sec = 0
                # store last values to show
                last_fps = fps
                last_bw = bw_kb
                last_pl = pl
            # overlay (use last_* if available)
            try:
                cv2.putText(img, f"FPS: {last_fps:.1f}", (10,25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                cv2.putText(img, f"BW: {last_bw:.1f} KB/s", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
                cv2.putText(img, f"Loss: {last_pl:.1f}%", (10,75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 1)
            except NameError:
                # first few frames may not have last_* set
                pass

            # show & write
            cv2.imshow("Live Stream", img)
            if video_writer is not None:
                video_writer.write(img)
        elif pkt_type == b'A':
            # audio: raw int16 bytes — play and save
            audio_stream.write(payload)
            audio_frames.append(payload)

        # keyboard
        if cv2.waitKey(1) == 27:
            break

except KeyboardInterrupt:
    pass

print("Stopping and saving files...")

# Close video writer
if video_writer is not None:
    video_writer.release()

# Save WAV audio
if len(audio_frames) > 0:
    wf = wave.open(OUT_AUDIO_FILE, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(audio_frames))
    wf.close()

audio_stream.stop_stream()
audio_stream.close()
pa.terminate()
sock.close()
cv2.destroyAllWindows()

print(f"Saved video: {OUT_VIDEO_FILE}")
if len(audio_frames)>0:
    print(f"Saved audio: {OUT_AUDIO_FILE}")
else:
    print("No audio recorded.")
