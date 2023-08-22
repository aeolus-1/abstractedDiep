var particles = []

function addParticle(options) {
    options = {
        pos:{x:0,y:0},
        color:"#000",
        size:0.1,
        duration:1.5,
        vel:{x:0,y:0},
        totalAlpha:0.8,
        ...options,
    }

    particles.push(options)
}

function spawnSparseParticle(cpos, range, options) {
    var angle = Math.random()*360,
        range = Math.random()*range,
        pos = {
            x:cpos.x+Math.cos(angle)*range,
            y:cpos.y+Math.sin(angle)*range,
        }

    addParticle({
        pos:pos,
        ...options,
    })
    
}

function renderParticles(delta) {
    for (let i = 0; i < particles.length; i++) {
        const particle = particles[i];
        particle.duration -= delta
        if (particle.duration<=0) {
            particles.splice(i, 1)
        } else {
            ctx.beginPath()

            ctx.arc(particle.pos.x,particle.pos.y,particle.size,0,Math.PI*2)

            ctx.globalAlpha = Math.max(Math.min(particle.duration,1),0)*particle.totalAlpha

            ctx.fillStyle = particle.color
            ctx.fill()

            ctx.closePath()
        }
    }
}