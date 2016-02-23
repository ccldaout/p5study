def textsetup():
    textFont(createFont("Edwardian Script ITC", 90))
    textMode(SHAPE)
    textAlign(CENTER, CENTER)
    
def message():
    cnt = 15
    for n in xrange(cnt):
        fill(color(50+n*(150/cnt), 0, 30))
        text("Happy Birthday", width/2, height*0.66, n)

def setup():
    size(600, 400, P3D)
    textsetup()
    blendMode(REPLACE)
    colorMode(RGB)

def action():
    cnt = 60
    for n in xrange(cnt):
        camera(0+(width/cnt)*n, height*0.9, 80, 250, 200, 0, 0, 1, 0)
        message()
        yield

action = action()

def draw():
    try:
        background(0)
        action.next()
    except StopIteration as e:
        noLoop()