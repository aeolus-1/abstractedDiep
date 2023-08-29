import asyncio
from aiohttp import web
import socketio
import random, time, json, base64
import threading

from game import Game

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*',  async_handlers=True)
app = web.Application()
sio.attach(app)

adminCode = open('admincode.txt').read()

global serverTps
serverTps = 0


TIMEOUT_DURATION = (60)  *1000


@sio.on('connect')
def connect(sid, environ):
    print("connected: ", sid)

@sio.on('join')
async def join(sid, environ):
    newClient = {
        "id":sid,
        "mobile":mainGame.addClientPlayer(sid, environ),
        "timeout":(time.time()*1000),
    }
    
    clients[sid] = newClient

    print("Player has Joined")

    await sio.emit("joined", {
        "mobId":newClient["mobile"].id,
        "sid":sid,
    }, to=sid)
    
@sio.on('requestTps')
async def message(sid, data):
    clientOb = clients.get(sid)
    if (clientOb):
        await sio.emit("returnTps", serverTps, to=sid, ignore_queue=True)

@sio.on('requestState')
async def message(sid, data):
    clientOb = clients.get(sid)
    if (clientOb):
        #print(sio.sendBuffer)
        await sio.emit("returnState", mainGame.getStateForClients(sid), to=sid, ignore_queue=True)
    else:
        await sio.emit("returnState", mainGame.getStateForSpectator(), to=sid, ignore_queue=True)
    # await asyncio.sleep(1 * random.random())
    # print('waited', data)

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)
    if (clients.get(sid)):
        clients[sid]["mobile"].disconnected = True
        mainGame.killMobile(clients[sid]["mobile"])
        clients[sid]["mobile"].duration = 0
    #clients[sid]["mobile"].bot = True

@sio.on('runCommand')
async def runCommand(sid, data):
    realCode = data["passcode"]
    if (realCode==adminCode):
        print("allowed Admin")
        mainGame.runCommand(data["code"])
    else:
        print("WARNING WARNING HACKER HACKER - kicking")
        print("pass tried: ", data["passcode"])
        print("code tried: ", data["code"])
        await sio.disconnect(sid)




@sio.on('submitKeys')
def submitKeys(sid, data):
    if clients.get(sid):
        clients[sid]["timeout"] = time.time()*1000
    mainGame.fetchMobile(data["mobId"]).keys = data["keys"]
    if (data["keys"].get("target")):
        mainGame.fetchMobile(data["mobId"]).target = data["keys"]["target"]


clients = {}


mainGame = Game()
mainGame.clients = clients
#        self.updatePlayerControls(delta)

def updateClientsGameState():
    global serverTps
    preTime = time.time()
    while True:
        serverTps = 1000/(((time.time()-preTime)*1000)+0.001)
        #print(tps)
        preTime = time.time()
        #print("emitting", time.time())
        mainGame.updateState(1/serverTps)

        deletions = []
        for client in clients:
            clientDict = clients[client]
            lastInteraction = (time.time()*1000)-clientDict["timeout"]
            if (lastInteraction>TIMEOUT_DURATION):
                print("disconnected mobile "+client+" for inactivity")
                mainGame.killMobile(clients[client]["mobile"])
                clients[client]["mobile"].duration = 0
                deletions.append(client)
        for i in deletions:
            del clients[i]
                



        time.sleep(1/30)

stateUpdater = threading.Thread(target=updateClientsGameState, args=())
stateUpdater.start()

def updatePlayerControls():
    preTime = time.time()
    while True:
        tps = 1000/(((time.time()-preTime)*1000)+0.001)
        #print(tps)
        preTime = time.time()
        #print("emitting", time.time())
        mainGame.updatePlayerControls(1/tps)
        time.sleep(1/30)

stateUpdater = threading.Thread(target=updatePlayerControls, args=())
stateUpdater.start()


if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=4545)