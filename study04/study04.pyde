def setup():
    size(300, 300)
    global img
    img = loadImage("drink_taru.png")

def draw():
    rw = float(width) / img.width
    rh = float(height) / img.height
    scale(min(rw, rh))
    image(img, 0, 0)
    noLoop()