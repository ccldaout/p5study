class SceneController(object):
    def __init__(self):
        self._gens = []
        self._loop = True
        
    def add_generator(self, gen):
        self._gens.append(gen)
        
    def step(self):
        nextgens = []
        for gen in self._gens:
            try:
                ret = gen.next()
                nextgens.append(gen)
                if isinstance(ret, (tuple, list)):
                    nextgens.extend(ret)
                elif ret is not None:
                    nextgens.append(ret)
            except StopIteration as e:
                pass
        self._gens = nextgens
        
    def toggle_loop(self):
        self._loop = not self._loop
        print 'toggle_loop:', self._loop
        if self._loop:
            loop()
        else:
            noLoop()
        
scene_controller = SceneController()

#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------

BG_COLOR_RGB = (0, 0, 0, 30)

def fade_background():
    noStroke()
    blendMode(BLEND)
    fill(*BG_COLOR_RGB)
    rectMode(SCREEN)
    rect(0, 0, width, height)
    
def createLight(isize, rPower, gPower, bPower):
    center = isize / 2.0
    img = createImage(isize, isize, RGB)
    for y in xrange(isize):
        for x in xrange(isize):
            factor = 3*exp(-((sq(center - x) + sq(center - y))/sq(isize/5)))
            r = int((255 * rPower) * factor)
            g = int((255 * gPower) * factor)
            b = int((255 * bPower) * factor)
            img.pixels[x + y * isize] = color(r, g, b)
    return img

def actor(lightimg, center_x, center_y, radius, stepangles):
    xang = yang = 0
    oang, ostep, xstep, ystep = stepangles
    scl = 1.0
    while True:
        pushMatrix()
        translate(center_x, center_y)
        rotateX(xang)
        rotateY(yang)
        translate(radius*cos(oang), radius*sin(oang))
        rotateY(-yang)
        rotateX(-xang)
        blendMode(LIGHTEST)
        scale(scl)
        image(lightimg, 0, 0)
        popMatrix()
        oang += ostep
        xang += xstep
        yang += ystep
        if abs(oang) > 3*TWO_PI:
            radius *= 0.99
            scl *= 0.99
            if scl < 0.05:
                return
        yield

#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------

def setup():
    #fullScreen(P3D)
    size(400, 400, P3D)
    hint(DISABLE_DEPTH_TEST)
    blendMode(ADD)
    imageMode(CENTER)
    background(*BG_COLOR_RGB[:3])
    scene_controller.add_generator(actor(createLight(100, 0.1, 0.5, 0.7),
                                         200, 200, 130,
                                         (HALF_PI, HALF_PI/40, 0.001, 0.005)))
    scene_controller.add_generator(actor(createLight(80, 0.9, 0.1, 0.2),
                                         200, 200, 110,
                                         (PI, HALF_PI/43, -0.001, 0.002)))
    scene_controller.add_generator(actor(createLight(50, 0.9, 0.9, 0.3),
                                         200, 200, 110,
                                         (-HALF_PI, -HALF_PI/30, -0.001, -0.002)))
    
def draw():
    fade_background()
    scene_controller.step()
    saveFrame("study02-####.tif")

def mousePressed():
    scene_controller.toggle_loop()