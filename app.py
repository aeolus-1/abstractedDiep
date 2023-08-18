import asyncio
from aiohttp import web
import socketio
import random, time, json
import threading

from game import Game

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*',  async_handlers=True)
app = web.Application()
sio.attach(app)


@sio.on('connect')
def connect(sid, environ):
    print("connected: ", sid)

@sio.on('join')
async def join(sid, environ):
    newClient = {
        "id":sid,
        "mobile":mainGame.addClientPlayer(sid)
    }
    clients[sid] = newClient

    print("Player has Joined")

    await sio.emit("joined", {
        "mobId":newClient["mobile"].id,
        "sid":sid,
    }, to=sid)


@sio.on('requestState')
async def message(sid, data):
    clientOb = clients.get(sid)
    if (clientOb):
        await sio.emit("returnState", mainGame.getStateForClients(sid), to=sid)
    else:
        pass#print("Non-joined player requesting")
    # await asyncio.sleep(1 * random.random())
    # print('waited', data)

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)



@sio.on('submitKeys')
def submitKeys(sid, data):
    mainGame.fetchMobile(data["mobId"]).keys = data["keys"]
    if (data["keys"].get("rotation")):
        mainGame.fetchMobile(data["mobId"]).rotation = data["keys"]["rotation"]


clients = {}


mainGame = Game()
mainGame.clients = clients

def updateClientsGameState():
    preTime = time.time()
    while True:
        tps = 1000/(((time.time()-preTime)*1000)+0.001)
        #print(tps)
        preTime = time.time()
        #print("emitting", time.time())
        mainGame.updateState(1/tps)
        time.sleep(1/30)

stateUpdater = threading.Thread(target=updateClientsGameState, args=())
stateUpdater.start()


if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=4545)