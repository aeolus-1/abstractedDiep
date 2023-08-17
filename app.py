import socketio
import eventlet
import time, threading, json

from game import Game

port = 6969
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = socketio.WSGIApp(sio, eventlet, static_files={
    '/': {'content_type': 'text/html', 'filename': 'client/index.html'},
    '/socket.io.min.js': {'content_type': 'text/html', 'filename': 'client/socket.io.min.js'},
    
})

@sio.on('connect')
def connect(sid, environ):
    print(f'Connected: {sid}')

@sio.on('requestState')
def connect(sid, environ):
    sio.emit("updateGameState", json.dumps(mainGame.getStateForClients()), )
    print(f'Connected: {sid}')

    #


def run():
    eventlet.wsgi.server(eventlet.listen(('', port)), app) # Note this line

mainGame = Game()

def updateClientsGameState():
    while True:
        #print("emitting", time.time())
        #Game.updateState()
        time.sleep(1/10)

stateUpdater = threading.Thread(target=updateClientsGameState, args=())
stateUpdater.start()

run()


