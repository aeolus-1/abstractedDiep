var cameraPos = [0,0],
    cameraRange = 0,
    deltaTime = (new Date()).getTime()

function renderLoop() {
    const gs = window.gameState,
        delta = (((((new Date()).getTime()-deltaTime)))/1000)



        
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

            wantedSize = cameraRange*(10/600),
            realScale = 1/Math.min(wantedSize/screenSize.x,wantedSize/screenSize.y)

        scale = realScale

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
            [15,15]
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

            if (!mob.bullet) {
                let currentEffects = Object.keys(mob.effects)
                for (let i = 0; i < currentEffects.length; i++) {
                    const effect = mob.effects[currentEffects[i]]
                    console.log("spawing")
                    if (Math.random()>0.8) spawnSparseParticle({x:mob.pos[0],y:mob.pos[1]},mob.build.size*(0.2/15)*2.5,{
                        color:effect.color,
                        duration:0.5,
                        size:((Math.random()*4)+8)*0.01
                    })
                }
            }
            
            

            if (dst < cameraRange*(10/600)) {
                    

                if (mob.friction>=1 && true){
                    mob.pos[0] += mob.vel[0]*delta
                    mob.pos[1] += mob.vel[1]*delta
                }
                ctx.globalAlpha = 1
                ctx.globalAlpha = Math.max(mob.opacity*mob.invis,mob.team==window.myTeam?0.3:0)
                ctx.save()
                

                let startPos = {x:mob.pos[0],y:mob.pos[1]},
                    rotation = mob.rotation

                ctx.translate(startPos.x,startPos.y)
                ctx.rotate(rotation)
                ctx.translate(-startPos.x,-startPos.y)


                function renderBarrel(rotation, offset, width, length) {
                    let radius = mob.build.size*(0.2/15),
                        xReach = Math.min(width/4,radius),
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
                    ctx.lineTo(startPos.x+backStep+length,startPos.y-xReach)
                    ctx.lineTo(startPos.x+backStep+length,startPos.y+xReach)
                    ctx.lineTo(startPos.x+rightBackStep,startPos.y+xReach)

                    let angleDiff = Math.atan2(xReach,backStep)
                    //ctx.arc(startPos.x,startPos.y,radius,angleDiff,angleDiff, true)

                    ctx.fillStyle = "#9d9d9d"
                    ctx.fill()

                    

                    ctx.closePath()

                    
                    

                

                    ctx.beginPath()

                    ctx.moveTo(startPos.x+leftBackStep,startPos.y-xReach)
                    
                    ctx.lineTo(startPos.x+backStep+length,startPos.y-xReach)
                    ctx.lineTo(startPos.x+backStep+length,startPos.y+xReach)

                    ctx.lineTo(startPos.x+rightBackStep,startPos.y+xReach)

                    ctx.strokeStyle = "#787878"
                    ctx.stroke()

                    ctx.closePath()

                    

                    ctx.restore()
                    

                }
                for (let i = 0; i < mob.build.guns.length; i++) {
                    const gun = mob.build.guns[i];
                    ctx.strokeStyle = "#000"
                    renderBarrel(gun.pos, gun.offset, 0.4*(gun.width/10),0.85*(gun.height/17))
                }

                ctx.beginPath()
                ctx.arc(mob.pos[0],mob.pos[1], mob.build.size*(0.2/15), 0, Math.PI*2)

                ctx.lineWidth = 3/100

                ctx.fillStyle = mob.team
                ctx.strokeStyle = pSBC(-0.4, mob.team)

                ctx.fill()
                ctx.stroke()
                ctx.closePath()
                    
                
                ctx.restore()

                ctx.globalAlpha *= 0.5
                let barWidth = 20/scale,
                    barHeight = ((0.7)+1) * mob.build.size*(0.2/15),
                    barThickness = 5

                function li(width) {
                    ctx.beginPath()
                    ctx.moveTo(startPos.x-barWidth,startPos.y-barHeight)
                    ctx.lineTo(startPos.x+barWidth-((1-width)*barWidth*2),startPos.y-barHeight)
                    ctx.stroke()
                    ctx.closePath()
                }

                if (!mob.bullet) {
                    ctx.lineCap = "round"

                    ctx.strokeStyle = "#777"
                    ctx.lineWidth = (barThickness*1.4)/scale
                    li(1)

                    ctx.strokeStyle = "#0f0"
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
    deltaTime = (new Date()).getTime()
    requestAnimationFrame(renderLoop)
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
document.addEventListener("keydown",(e)=>{keys[e.code]=true;updateServerKeys()})
document.addEventListener("keyup",(e)=>{keys[e.code]=false;updateServerKeys()})

document.addEventListener("mousedown",(e)=>{keys["mouseDown"]=true;updateServerKeys()})
document.addEventListener("mouseup",(e)=>{keys["mouseDown"]=false;updateServerKeys()})

document.addEventListener("mousemove",(e)=>{
    let inGamePos = {
        x:e.offsetX-(canvas.width/2),
        y:e.offsetY-(canvas.height/2),
    }
    keys.rotation = Math.atan2(
        inGamePos.y,
        inGamePos.x
    )
    ;updateServerKeys()})

