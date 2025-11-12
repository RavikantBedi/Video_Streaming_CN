# 🎥 UDP Real-Time Video & Audio Streaming  
**Team: GeekPro**

A lightweight real-time video and audio streaming application using **Python, OpenCV, PyAudio and UDP sockets**.  
It supports **low-latency live streaming**, **audio playback**, **video recording**, **packet statistics (FPS, Bandwidth, Loss%)**, and **auto-saving of received streams**.

---

## 🚀 Features

✔ Live **Video + Audio streaming** over UDP  
✔ Low latency transmission using compressed JPEG frames  
✔ Real-time **stats overlay** (FPS, bandwidth, packet loss)  
✔ **Automatic recording** of received video + audio  
✔ Noise-gated and normalized audio streaming  
✔ UDP handshake for client discovery  
✔ Dynamic video window resizing  
✔ Cross-platform support (Windows, Linux, Mac)

---

## 🛠 Tech Stack

| Component | Technology |
|---------|-----------|
| Language | Python 3.x |
| Networking | UDP Sockets |
| Video Processing | OpenCV |
| Audio | PyAudio |
| Serialization | Pickle |
| Compression | JPEG (OpenCV) |

---

## 📦 Required Libraries

Install all dependencies using:

```sh
pip install opencv-python numpy pyaudio

⚠ If PyAudio installation fails on Windows, install manually:

pip install pipwin
pipwin install pyaudio

🧠 How It Works
1. Server

Captures webcam video + microphone audio

Compresses video using JPEG

Applies noise-gating & normalization to audio

Sends packets over UDP with custom header:

[Type (1 byte)] + [Payload Size (8 bytes)] + [Data]


V → Video Frame

A → Audio Frame

2. Client

Sends handshake (hello) to server

Receives packets, decodes video & plays audio

Displays stream with overlay stats

Saves video (.avi) and audio (.wav)

▶️ Run the Project
Start Server
python server.py

Start Client
python client.py


When prompted, enter server IP:

Enter Server IP: 192.168.x.x


Press ESC to stop and save recordings.

📁 Output Files Generated

After stopping the stream, client auto-saves:

File	Description
recorded_<timestamp>.avi	Saved video stream
audio_<timestamp>.wav	Saved audio stream
📊 Live Stream Statistics

Overlay included on client window:

FPS: 19.8
BW: 450 KB/s
Loss: 4.2%

🧩 Packet Structure
Section	Size	Purpose
Type	1 byte	V (video) / A (audio)
Length	8 bytes	Actual payload size
Payload	N bytes	Pickle JPEG / Raw audio
⚙️ Tunable Parameters
Parameter	Purpose
JPEG_QUALITY	Video compression vs quality
RATE	Audio sampling rate
CHUNK	Audio frames per packet
AUDIO_THRESHOLD	Noise filter level
VIDEO_FPS	Output recording frame rate
📸 UI Preview
Client Display	Server Console
Live video window with overlay stats	Connection logs + streaming status
❗ Known Limitations

UDP may drop packets on weak networks (shown in stats)

No encryption (raw UDP stream)

Works best on local Wi-Fi/LAN

Single client currently supported

💡 Future Enhancements

🔹 Multi-client broadcasting
🔹 Forward error correction (FEC)
🔹 Encryption (SRTP/DTLS)
🔹 Web client support using WebRTC

👨‍💻 Contributors
Name	Role
Team Ravikant Bedi -->	Backend & Network Developer
Team Dev Saxena --> Client-Side Engineer
Team Sushant Kanijiya  -->Testing & Documentation Engineer
📜 License

MIT License © 2025 GeekPro