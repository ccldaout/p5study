def textsetup():
    textFont(createFont("Edwardian Script ITC", 90))
    textMode(SHAPE)
    textAlign(CENTER, CENTER)
    
def message():
    cnt = 15
    for n in xrange(cnt):
        fill(color(50+n*(150/cnt), 0, 30))
        text("Happy Birthday", width/2, height/2, n)

def setup():
    size(550, 200, P3D)
    textsetup()
    blendMode(REPLACE)
    colorMode(RGB)

def action():
    cnt = 50
    for n in xrange(cnt):
        camera(50+(450/cnt)*n, 120, 50, 250, 150, 0, 0, 1, 0)
        message()
        yield

action = action()

def draw():
    try:
        background(0)
        action.next()
    except StopIteration as e:
        noLoop()
