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

_r3 = sqrt(3)

def create_star6(w, color_prm, ang=0):
    star = createShape(GROUP)
    hw = w/2
    hwr3 = hw * _r3
    invhwr3 = hw / _r3
    noStroke()
    t1 = createShape(TRIANGLE, 0, 0, w, 0, hw, -hwr3)
    t1.translate(-hw, invhwr3)
    t1.setFill(color(*color_prm))
    t2 = createShape(TRIANGLE, 0, 0, w, 0, hw, hwr3)
    t2.translate(-hw, -invhwr3)
    t2.setFill(color(*color_prm))
    star.addChild(t1)
    star.addChild(t2)
    star.rotate(ang)
    return star

def fade_background():
    noStroke()
    blendMode(BLEND)
    fill(*BG_COLOR_RGB)
    rectMode(SCREEN)
    rect(0, 0, width, height)
    
def create_light(isize, rPower, gPower, bPower):
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

def particles(radius, oang, ostep, scl):
    cnt = 200
    for _ in xrange(cnt):
        r = radius + 8 * (randomGaussian() - 0.5)
        o = oang - (ostep * random(4, 120))
    	x, y = r * cos(o), r * sin(o)
	w = scl * random(1, 8)
	shape(star6, x, y, w, w)	

def actor(lightimg, center_x, center_y, radius, stepangles):
    xang = yang = 0
    oang, ostep, xstep, ystep = stepangles
    scl = 1.0
    while True:
             
        pushMatrix()
        blendMode(ADD)
        translate(center_x, center_y)
        rotateX(xang)
        rotateY(yang)
        #translate(radius*cos(oang), radius*sin(oang))
        #rotateX(-xang)
        #rotateY(-yang)
        #scale(scl)
        particles(radius, oang, ostep, scl)
        popMatrix()
        
        pushMatrix()
        blendMode(LIGHTEST)        
        translate(center_x, center_y)
        oang += ostep
        xang += xstep
        yang += ystep        
        rotateX(xang)
        rotateY(yang)
        translate(radius*cos(oang), radius*sin(oang))
        rotateY(-yang)
        rotateX(-xang)
        scale(scl)
        image(lightimg, 0, 0)
        popMatrix()
        
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
    global star6
    star6 = create_star6(20, (120, 120, 120, 30), ang=HALF_PI/8)
    steps = [-0.007, -0.004, 0.003, 0.007]
    sign = [1, -1]
    for i in xrange(10):
        light = create_light(100, random(0.1, 0.9), random(0.1, 0.9), random(0.1, 0.9))
        scene_controller.add_generator(actor(light,
                                             width/2, height/2, 140,
                                             (random(0, TWO_PI),
                                              sign[i % 2] * HALF_PI/40,
                                              steps[int(random(len(steps)-0.9))],
                                              steps[int(random(len(steps)-0.9))])))
    
def draw():
    fade_background()
    scene_controller.step()
    saveFrame("study-####.tif")

def mousePressed():
    scene_controller.toggle_loop()