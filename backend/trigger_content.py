from flask_socketio import SocketIO
import eventlet

# Create a socket connection (ensure this matches your backend)
socketio = SocketIO(cors_allowed_origins="*")

# Manually emit WebSocket event
socketio.emit("content_ready", {
    "videoUrl": "https://your-video-url.com/sample.mp4",
    "insightsUrl": "https://your-insights-url.com/sample.json"
}, namespace='/')

print("✅ Manually triggered WebSocket event!")
