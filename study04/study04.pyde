def setup():
    size(500, 200, P3D)
    background(0)
    textFont(createFont("Edwardian Script ITC", 100))
    textMode(SHAPE)
    textAlign(CENTER, CENTER)
    fill(255)
    blendMode(REPLACE)
    camera(250, 110, 300, 250, 100, 50, 0, -1, 0)

def action():
    for n in xrange(10):
        text("Happy Birthday", width/2, height/2, n*2)
        yield

action = action()

def draw():
    try:
        action.next()
    except:
        noLoop()