#----------------------------------------------------------------------------------------------
# common 
#----------------------------------------------------------------------------------------------

import inspect as _ins
_ATTR_INITIAL_ACTOR = '_initial_actor_'

SIZE_PARAMS = (300, 300, P2D)

_controller_object = None

def fade_background():
    noStroke()
    blendMode(BLEND)
    fill(*BG_COLOR_RGB)
    rectMode(SCREEN)
    rect(0, 0, width, height)

def add_actor():
    n = [0]
    def _add_actor(f):
        setattr(f, _ATTR_INITIAL_ACTOR, n[0])
        n[0] += 1
        return f
    return _add_actor
add_actor = add_actor()
    
def setup_controller(controller_class):
    controller = controller_class()
    global _controller_object
    _controller_object = controller
    return controller_class

class BaseController(object):
    def __new__(cls):
        self = super(BaseController, cls).__new__(cls)
        self._loop = True
        self.save_frame = False
        self._acts = []
        def get_actors():
            for _, attr in _ins.getmembers(self):
                if hasattr(attr, _ATTR_INITIAL_ACTOR):
                    yield getattr(attr, _ATTR_INITIAL_ACTOR), attr
        for _, attr in sorted(list(get_actors())):
            self.add_actor(attr)
        return self

    def __generator(self, func):
        while True:
            func()
            yield
        
    def add_actor(self, obj):
        if _ins.isgenerator(obj):
            self._acts.append(obj)
        elif _ins.isgeneratorfunction(obj):
            self._acts.append(obj())
        elif callable(obj):
            self._acts.append(self.__generator(obj))
        else:
            raise Exception('obj must be one of generator/generator function/function')
        
    def __step(self):
        nextacts = []
        for gen in self._acts:
            try:
                ret = gen.next()
                nextacts.append(gen)
                if isinstance(ret, (tuple, list)):
                    nextacts.extend(ret)
                elif ret is not None:
                    nextacts.append(ret)
            except StopIteration as e:
                pass
        self._acts = nextacts
        
    def __toggle_loop(self):
        self._loop = not self._loop
        print 'toggle_loop:', self._loop
        if self._loop:
            loop()
        else:
            noLoop()

    def mousePressed(self):
        self.__toggle_loop()
        
    def mysetup(self):
        pass

    def setup(self):
        self.mysetup()

    def pre_draw(self):
        pass

    def draw(self):
        self.pre_draw()
        self.__step()
        if self.save_frame:
            saveFrame("frame-####.tif")
 
def setup():
    # [REMARK] The size() must be at first line of setup function.
    size(*SIZE_PARAMS)
    _controller_object.setup()

def draw():
    _controller_object.draw()

def mousePressed():
    _controller_object.mousePressed()

#----------------------------------------------------------------------------------------------
# application
#----------------------------------------------------------------------------------------------

SIZE_PARAMS = (400, 400, P3D)
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
    cnt = 100
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

@setup_controller
class Controller(BaseController):

    def mysetup(self):
        hint(DISABLE_DEPTH_TEST)
        blendMode(ADD)
        imageMode(CENTER)
        background(*BG_COLOR_RGB[:3])
        global star6
        star6 = create_star6(20, (120, 120, 120, 30), ang=HALF_PI/8)
        steps = [-0.007, -0.006, -0.005, -0.004, 0.004, 0.005, 0.006, 0.007]
        sign = [1, -1]
        for i in xrange(20):
            light = create_light(40,
                                 random(0.1, 0.9),
                                 random(0.1, 0.9),
                                 random(0.1, 0.9))
            self.add_actor(actor(light,
                                 width/2, height/2,
                                140,
                                 (random(0, TWO_PI),
                                  sign[i % 2] * HALF_PI/40,
                                  steps[int(random(len(steps)-0.9))],
                                  steps[int(random(len(steps)-0.9))])))
    
    def pre_draw(self):
        fade_background()