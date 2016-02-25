#----------------------------------------------------------------------------
# common - personal framework
#----------------------------------------------------------------------------

_ATTR_INITIAL_ACTOR = '_initial_actor_'

def add_actor():
    n = [0]
    def _add_actor(f):
        setattr(f, _ATTR_INITIAL_ACTOR, n[0])
        n[0] += 1
        return f
    return _add_actor
add_actor = add_actor()
    
def setup_controller(width, height, mode=P2D, save_fps=0.0):
    global _size_params
    _size_params = (width, height, mode)
    def _setup(controller_class):
        controller = controller_class(save_fps)
        global _controller_object
        _controller_object = controller
        return controller_class
    return _setup
    
class BaseController(object):
    import inspect as __inspect
    
    def __new__(cls, save_fps):
        self = super(BaseController, cls).__new__(cls)
        self.__loop = True
        if save_fps < 1.0:
            self.fps = 10
            self.__save_frame = False
        else:
            self.fps = save_fps
            self.__save_frame = True
        self.__acts = []
        def get_actors():
            import inspect
            for _, attr in self.__inspect.getmembers(self):
                if hasattr(attr, _ATTR_INITIAL_ACTOR):
                    yield getattr(attr, _ATTR_INITIAL_ACTOR), attr
        for _, attr in sorted(list(get_actors())):
            self.add_actor(attr)
        return self

    def __generator(self, func):
        while func():
            yield
        
    def add_actor(self, obj):
        if self.__inspect.isgenerator(obj):
            self.__acts.append(obj)
        elif self.__inspect.isgeneratorfunction(obj):
            self.__acts.append(obj())
        elif callable(obj):
            self.__acts.append(self.__generator(obj))
        else:
            raise Exception('obj must be one of generator/generator function/function')
        
    def __step(self):
        nextacts = []
        for gen in self.__acts:
            try:
                ret = gen.next()
                nextacts.append(gen)
                if isinstance(ret, (tuple, list)):
                    nextacts.extend(ret)
                elif ret is not None:
                    nextacts.append(ret)
            except StopIteration as e:
                pass
        self.__acts = nextacts
        
    def __toggle_loop(self):
        self.__loop = not self.__loop
        print 'toggle_loop:', self.__loop
        if self.__loop:
            loop()
        else:
            noLoop()

    def mousePressed(self):
        self.__toggle_loop()
        
    def mysetup(self):
        pass

    def setup(self):
        frameRate(self.fps)
        self.mysetup()

    def pre_draw(self):
        pass

    def draw(self):
        self.pre_draw()
        self.__step()
        if self.__save_frame:
            saveFrame("frame-#####.tif")
 
def setup():
    # [REMARK] The size() must be at first line of setup function.
    size(*_size_params)
    _controller_object.setup()

def draw():
    _controller_object.draw()

def mousePressed():
    _controller_object.mousePressed()

def fade_background(bgcolor=color(0,10)):
    noStroke()
    blendMode(BLEND)
    fill(bgcolor)
    rectMode(CORNER)
    rect(0, 0, width, height)

def curve3(x):
    x = 2*x - 1
    return 0.5 - x * (x*x - 3) / 4

def curve5(x):
    x3 = x * x * x
    x4 = x3 * x
    x5 = x4 * x
    return 6*x5 - 15*x4 + 10*x3

def range_curved(n, curve=curve5):
    n -= 1
    for i in xrange(n+1):
        x = float(i)/n
        y = curve(x)
        yield i, y

#----------------------------------------------------------------------------
# application
#----------------------------------------------------------------------------

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

@setup_controller(400, 400, P3D, save_fps=0.0)
class Controller(BaseController):

    def mysetup(self):
        hint(DISABLE_DEPTH_TEST)
        blendMode(ADD)
        imageMode(CENTER)
        frameRate(30)
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
        fade_background(color(*BG_COLOR_RGB))
