import socketio
import eventlet
import time, threading
import json

port = 6969
sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'client/index.html'},
    '/socket.io.min.js': {'content_type': 'text/javascript', 'filename': 'client/socket.io.min.js'},
    '/main.js': {'content_type': 'text/javascript', 'filename': 'client/main.js'},
    
})

def run():
    eventlet.wsgi.server(eventlet.listen(('', port)), app, debug=True) # Note this line

run()