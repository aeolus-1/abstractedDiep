var cameraPos = [0,0]

function renderLoop() {
    const gs = window.gameState
    if (gs!=undefined&&socket.connected) {

        for (let i = 0; i < gs.players.length; i++) {
            const player = gs.players[i];
            //console.log(player.keys.rotation)
        }


        ctx.save()

        ctx.clearRect(0,0,canvas.width,canvas.height)
        //ctx.translate(canvas.width/2,canvas.height/2)

        //ctx.translate(-canvas.width/2,-canvas.height/2)
        let scale = 100
        ctx.scale(scale,scale)
        
        ctx.translate(canvas.width*0.5*(1/scale),canvas.height*0.5*(1/scale))
        ctx.translate(-cameraPos[0],-cameraPos[1])
        totalMobiles = [...gs.mobiles,...gs.players]
        for (let i = 0; i < totalMobiles.length; i++) {
            const mob = totalMobiles[i];
            
            ctx.save()

            ctx.beginPath()
            ctx.arc(mob.pos[0],mob.pos[1], mob.radius, 0, Math.PI*2)

            ctx.lineWidth = 3/scale
            ctx.stroke()
            ctx.closePath()
                
            let startPos = {x:mob.pos[0],y:mob.pos[1]},
                rotation = mob.rotation

            ctx.translate(startPos.x,startPos.y)
            ctx.rotate(rotation)
            ctx.translate(-startPos.x,-startPos.y)


            function renderBarrel(rotation, width, length) {
                let radius = mob.build.size*(0.2/15),
                    xReach = Math.min(width/4,radius),
                    backStep = Math.sqrt(Math.pow(radius,2)-Math.pow(xReach,2))
                length = length*radius*2

                ctx.save()

                ctx.translate(startPos.x,startPos.y)
                ctx.rotate(rotation*(Math.PI/180))
                ctx.translate(-startPos.x,-startPos.y)

                ctx.beginPath()
                
                ctx.moveTo(startPos.x+backStep,startPos.y-xReach)
                
                ctx.lineTo(startPos.x+backStep+length,startPos.y-xReach)
                ctx.lineTo(startPos.x+backStep+length,startPos.y+xReach)

                ctx.lineTo(startPos.x+backStep,startPos.y+xReach)

                ctx.stroke()
                ctx.closePath()

                ctx.restore()
                

            }
            for (let i = 0; i < mob.build.guns.length; i++) {
                const gun = mob.build.guns[i];
                renderBarrel(gun.pos, 0.4*(gun.width/10),0.85*(gun.height/17))
            }
            
            






            ctx.restore()
        }

        ctx.restore()
    }
    requestAnimationFrame(renderLoop)
}

function updateServerKeys(){
    if (socket) if (socket.connected) socket.emit("submitKeys", {
        keys:keys,
        mobId:MOBILE_ID,
    })
}

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

