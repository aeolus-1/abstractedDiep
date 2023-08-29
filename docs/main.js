var cameraPos = [0,0],
    cameraRange = 0,
    deltaTime = (new Date()).getTime()

function renderLoop() {
    const gs = window.gameState,
        delta = (((((new Date()).getTime()-deltaTime)))/1000)

    ctx.lineJoin = "round"

        
    if (gs!=undefined&&socket.connected) {

        for (let i = 0; i < gs.players.length; i++) {
            const player = gs.players[i];
            //console.log(player.keys.rotation)
        }
        
        let scale = 1,

            screenSize = {
                x:canvas.width*0.5*(1/scale),
                y:canvas.height*0.5*(1/scale),
            },

            wantedSize = cameraRange*(7/600),
            realScale = 1/Math.min(wantedSize/screenSize.x,wantedSize/screenSize.y)

        scale = realScale
        window.globalScale = scale

        ctx.save()

        ctx.fillStyle = "#bbb"
        ctx.fillRect(0,0,canvas.width,canvas.height)

        
        //ctx.translate(canvas.width/2,canvas.height/2)

        //ctx.translate(-canvas.width/2,-canvas.height/2)
        
        ctx.scale(scale,scale)
        
        ctx.translate(canvas.width*0.5*(1/scale),canvas.height*0.5*(1/scale))
        ctx.translate(-cameraPos[0],-cameraPos[1])

        bounds = [
            [-5,-5],
            [gs.bounds[0],gs.bounds[1]]
        ]
        ctx.fillStyle = "#fff"
        ctx.fillRect(bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1])

        function drawGrid(size) {
            let grid = size,
                c = {x:cameraPos[0],y:cameraPos[1]},
                v = (x=0,y=0)=>{return {x:x,y:y}}
    
    
            let mod = v(
                (Math.floor(c.x/grid)*grid)*0,
                (Math.floor(c.y/grid)*grid)*0
                )
    
    
            var bu = 0,
                dim = v(
                    0.5*((window.innerWidth) / grid),
                    0.5*((window.innerHeight) / grid)
                )
    
            for (let i = -bu+-dim.x; i < (dim.x*2)+bu; i++) {
                ctx.beginPath()
                ctx.moveTo((i * grid) + mod.x, -dim.y+mod.y-(bu*grid))
    
                ctx.lineTo(i * grid + mod.x, (window.innerHeight) + mod.y + (bu*grid))
    
                ctx.closePath()
    
                ctx.stroke()
            }
            
            for (let i = -bu+-dim.y; i < (dim.y*2)+bu; i++) {
                ctx.beginPath()
                ctx.moveTo(-dim.x+mod.x-(bu*grid), i * grid + mod.y)
    
                ctx.lineTo((window.innerWidth+(bu*grid)) + mod.x, i * grid + mod.y)
    
                ctx.closePath()
    
                ctx.stroke()
            }
        }

        ctx.lineWidth = 1/scale
        ctx.strokeStyle = "#9995"
        drawGrid(0.3)


        renderParticles(delta)



        ctx.strokeStyle = "#000"
        totalMobiles = [...gs.mobiles,...gs.players]
        for (let i = 0; i < totalMobiles.length; i++) {
            const mob = totalMobiles[i];
            let dst = Math.sqrt(Math.pow(mob.pos[0]-cameraPos[0],2)+Math.pow(mob.pos[1]-cameraPos[1],2))

            if (!mob.bullet&&!mob.poly) {
                let currentEffects = Object.keys(mob.effects)
                for (let i = 0; i < currentEffects.length; i++) {
                    const effect = mob.effects[currentEffects[i]]
                    console.log("spawing")
                    if (Math.random()>0.8) spawnSparseParticle({x:mob.pos[0],y:mob.pos[1]},mob.build.size*2.5,{
                        color:effect.color,
                        duration:0.5,
                        size:((Math.random()*4)+8)*0.01
                    })
                }
            }
            
            

            if (dst < cameraRange*(10/600)) {
                    

                if (true){
                    mob.pos[0] += mob.vel[0]*delta
                    mob.pos[1] += mob.vel[1]*delta

                    mob.vel[0] *= Math.pow(mob.friction, delta)
                    mob.vel[1] *= Math.pow(mob.friction, delta)
                }
                ctx.globalAlpha = 1
                ctx.globalAlpha = Math.max(mob.opacity*mob.invis,mob.team==window.myTeam?0.3:0)
                ctx.save()
                

                let startPos = {x:mob.pos[0],y:mob.pos[1]},
                    rotation = mob.rotation

                ctx.translate(startPos.x,startPos.y)
                ctx.rotate(rotation)
                ctx.translate(-startPos.x,-startPos.y)


                function renderBarrel(rotation, offset, width, endWidth, length) {
                    let radius = mob.build.size,
                        xReach = Math.min(width/4,radius),
                        xReachEnd = endWidth/4
                        backStep = Math.sqrt(Math.pow(radius,2)-Math.pow(xReach,2))

                    offset = offset*radius*2
                    length = length*radius*2

                    ctx.save()

                    ctx.translate(startPos.x,startPos.y)
                    ctx.rotate(rotation*(Math.PI/180))
                    ctx.translate(-startPos.x,-startPos.y)

                    ctx.translate(0,offset)


                    ctx.lineWidth = 3/100

                    function mapXToCirle(y) {
                        return Math.sqrt(Math.pow(radius,2)-Math.pow(y,2))
                    }

                    let leftBackStep = mapXToCirle(-xReach+offset),
                        rightBackStep = mapXToCirle(xReach+offset)
                    


                    ctx.beginPath()

                    ctx.moveTo(startPos.x+leftBackStep,startPos.y-xReach)
                    ctx.lineTo(startPos.x+backStep+length,startPos.y-xReachEnd)
                    ctx.lineTo(startPos.x+backStep+length,startPos.y+xReachEnd)
                    ctx.lineTo(startPos.x+rightBackStep,startPos.y+xReach)

                    let angleDiff = Math.atan2(xReach,backStep)
                    //ctx.arc(startPos.x,startPos.y,radius,angleDiff,angleDiff, true)

                    ctx.fillStyle = "#999999"
                    ctx.fill()

                    

                    ctx.closePath()

                    

                

                    ctx.beginPath()

                    ctx.moveTo(startPos.x+leftBackStep,startPos.y-xReach)
                    
                    ctx.lineTo(startPos.x+backStep+length,startPos.y-xReachEnd)
                    ctx.lineTo(startPos.x+backStep+length,startPos.y+xReachEnd)

                    ctx.lineTo(startPos.x+rightBackStep,startPos.y+xReach)

                    ctx.strokeStyle = "#727272"
                    ctx.stroke()

                    ctx.closePath()

                    

                    ctx.restore()
                    

                }
                for (let i = 0; i < mob.build.guns.length; i++) {
                    const gun = mob.build.guns[i];
                    ctx.strokeStyle = "#000"
                    renderBarrel(gun.pos, gun.offset, 0.4*(gun.width/10), (gun.endWidth)?0.4*(gun.endWidth/10):0.4*(gun.width/10),0.85*(gun.height/17))
                }

                ctx.beginPath()
                if (mob.build.sides==undefined||mob.build.sides<=1){
                    ctx.arc(mob.pos[0],mob.pos[1], mob.build.size, 0, Math.PI*2)
                } else {
                    let rad = mob.build.size
                    ctx.moveTo(mob.pos[0]+rad,mob.pos[1])
                    for (let i = 1; i < mob.build.sides+1; i++) {
                        let pointAngle = (i/mob.build.sides)*Math.PI*2
                        ctx.lineTo(
                            mob.pos[0]+Math.cos(pointAngle)*rad,
                            mob.pos[1]+Math.sin(pointAngle)*rad
                        )
                    }
                }
                

                ctx.lineWidth = 3/100

                let lighten = 0//mob.poly?0:0.05
                ctx.fillStyle = pSBC(lighten,mob.team)
                ctx.strokeStyle = pSBC(lighten,pSBC(-0.4, mob.team))

                ctx.fill()
                ctx.stroke()
                ctx.closePath()
                    
                
                ctx.restore()

                //ctx.globalAlpha *= 0.5
                let barWidth = 20/scale,
                    barHeight = ((0.7)+1) * mob.build.size,
                    barThickness = 5

                function li(width) {
                    ctx.beginPath()
                    ctx.moveTo(startPos.x-barWidth,startPos.y-barHeight)
                    ctx.lineTo(startPos.x+barWidth-((1-width)*barWidth*2),startPos.y-barHeight)
                    ctx.stroke()
                    ctx.closePath()
                }

                if (!mob.bullet&&mob.health<0.99) {
                    ctx.lineCap = "round"

                    ctx.strokeStyle = "#545454"
                    ctx.lineWidth = (barThickness*1.4)/scale
                    li(1)

                    ctx.strokeStyle = "#86c280"
                    ctx.lineWidth = (barThickness)/scale
                    li(Math.min(Math.max(mob.health,0),1))
                }
            }
    
            
            






            
        }


        
        ctx.restore()
    }

    ctx.font = "Arial 40px"
    ctx.fillStyle = "#000"
    ctx.fillText("Server Tps: "+Math.round(window.serverTps), 10,10)
    ctx.fillText("Ping: "+Math.round(window.serverPing), 10,20)



    renderLeaderBoard(window.leaderboard)
    
    let margin = 30,
        barWidth = 200,
        barThickness = barWidth * (1/6)

    let barPos = {
        x:window.innerWidth/2,
        y:window.innerHeight-margin
    }

    ctx.beginPath()
    ctx.moveTo(barPos.x-(barWidth*0.5),barPos.y)
    ctx.lineTo(barPos.x+(barWidth*0.5),barPos.y)

    ctx.strokeStyle = "#727272"
    ctx.lineWidth = barThickness*1.4
    ctx.stroke()
    
    ctx.strokeStyle = "#0bf"
    ctx.lineWidth = barThickness
    ctx.stroke()

    ctx.closePath()

    let fontSize = barThickness*0.7
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'center';
    ctx.font = `${fontSize}px Ubuntu`

    let text = window.xp

    ctx.strokeStyle = "#000"
    ctx.fillStyle = "#fff"

    ctx.lineWidth = fontSize*0.2
    ctx.strokeText(text, barPos.x,barPos.y)
    ctx.fillText(text, barPos.x,barPos.y)



    deltaTime = (new Date()).getTime()
    requestAnimationFrame(renderLoop)
}

function renderLeaderBoard(board) {
    boardNames = Object.keys(board).sort((a,b)=>{return -(board[a]-board[b])})

    let barWidth = 120,
        barThickness = 20,
        margin = 10

    let startPos = {
        x:window.innerWidth-(barWidth)-margin-margin,
        y:(barThickness*0.5)+margin,
    }

    for (let i = 0; i < boardNames.length; i++) {
        const entre = boardNames[i];
        let name = entre,
            num = board[name]
        
        let y= i*barThickness*1.1

        ctx.beginPath()
        ctx.moveTo(startPos.x-barWidth,startPos.y+y)
        ctx.lineTo(startPos.x+barWidth,startPos.y+y)

        ctx.lineWidth = barThickness
        ctx.lineCap = "round"
        
        ctx.strokeStyle = "#545454"
        ctx.stroke()
        ctx.closePath()

        let fullness = num/board[boardNames[0]]

        

        ctx.beginPath()
        ctx.moveTo(startPos.x-barWidth,startPos.y+y)
        ctx.lineTo(startPos.x+-barWidth+(fullness*barWidth*2),startPos.y+y)

        ctx.lineWidth = barThickness*0.8
        ctx.lineCap = "round"
        
        ctx.strokeStyle = "#f00"
        ctx.stroke()
        ctx.closePath()

        let fontSize = barThickness*0.7
        ctx.textBaseline = 'middle';
        ctx.textAlign = 'center';
        ctx.font = `${fontSize}px Ubuntu`

        ctx.fillStyle = "#fff"
        ctx.strokeStyle = "#000"
        ctx.lineWidth = fontSize*0.2
        ctx.strokeText(name, startPos.x,startPos.y+y)
        ctx.fillText(name, startPos.x,startPos.y+y)



    }

}

var lastInteracted = (new Date()).getTime()

function updateServerKeys(){
    if (socket) if (socket.connected) socket.emit("submitKeys", {
        keys:keys,
        mobId:MOBILE_ID,
    })
    lastInteracted = (new Date()).getTime()
}
setInterval(() => {
    if ((new Date()).getTime-lastInteracted>30000){
        alert("likely disconnected due to inactivity\ni'm not 100% sure")
    }
}, 15);

var keys = {}
document.addEventListener("keydown",(e)=>{
    let code = e.code
    if (code=="ArrowLeft") code = "KeyA"
    if (code=="ArrowRight") code = "KeyD"
    if (code=="ArrowUp") code = "KeyW"
    if (code=="ArrowDown") code = "KeyS"
    keys[code]=true;updateServerKeys()
})
document.addEventListener("keyup",(e)=>{
    let code = e.code
    if (code=="ArrowLeft") code = "KeyA"
    if (code=="ArrowRight") code = "KeyD"
    if (code=="ArrowUp") code = "KeyW"
    if (code=="ArrowDown") code = "KeyS"
    keys[code]=false;updateServerKeys()
})

document.addEventListener("mousedown",(e)=>{keys["mouseDown"]=true;updateServerKeys()})
document.addEventListener("mouseup",(e)=>{keys["mouseDown"]=false;updateServerKeys()})

document.addEventListener("mousemove",(e)=>{
    let inGamePos = {
        x:e.offsetX-(canvas.width/2),
        y:e.offsetY-(canvas.height/2),
    }
    keys.target = [
        inGamePos.x/globalScale,
        inGamePos.y/globalScale,   
    ]
    ;updateServerKeys()})

