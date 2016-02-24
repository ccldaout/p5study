#----------------------------------------------------------------------------------------------
# common 
#----------------------------------------------------------------------------------------------

import inspect as _ins
_ATTR_INITIAL_ACTOR = '_initial_actor_'

SIZE_PARAMS = (300, 300, P2D)

_controller_object = None

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
            if not func():
                return
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

def fade_background(bgcolor=color(0,10)):
    noStroke()
    blendMode(BLEND)
    fill(bgcolor)
    rectMode(SCREEN)
    rect(0, 0, width, height)

def movement_curve(x):
    x = 2*x - 1
    return 0.5 - x * (x*x - 3) / 4

def range_curved(n, curve=movement_curve):
    n -= 1
    for i in xrange(n+1):
        x = float(i)/n
        y = curve(x)
        yield i, y

#----------------------------------------------------------------------------------------------
# application
#----------------------------------------------------------------------------------------------

SIZE_PARAMS = (600, 400, P3D)

@setup_controller
class Controller(BaseController):

    def mysetup(self):
        self._fps = 10
        frameRate(self._fps)
        blendMode(REPLACE)
        colorMode(HSB, 360, 100, 100)
        textFont(createFont("Edwardian Script ITC", 90))
        textMode(SHAPE)
        textAlign(CENTER, CENTER)
        #self.save_frame = True
        self._b_ratio = 0.0
        self._fadeout = False

    def pre_draw(self):
        background(0)

    @add_actor
    def camera(self):
        foc_x, foc_y, foc_z = width/2, height/2, 0
        eye_x, eye_y, eye_z = 0, height*0.8, 80

        cnt = self._fps * 6
        for _, ratio in range_curved(cnt):
            eye_x = width * ratio
            camera(eye_x, eye_y, eye_z, foc_x, foc_y, foc_z, 0, 1, 0)
            yield

        cnt = self._fps * 3
        for _, ratio in range_curved(cnt):
            eye_x = width * (1 - 0.5 * ratio)
            eye_y = height*0.8 * (1 - ratio)
            camera(eye_x, eye_y, eye_z, foc_x, foc_y, foc_z, 0, 1, 0)
            yield

        cnt = self._fps * 6
        inifoc_y = foc_y
        endfoc_y = height*0.7 
        for _, ratio in range_curved(cnt):
            self._b_ratio = ratio
            eye_y = height*0.8 * ratio
            eye_z = 80 + (300 - 80) * ratio
            foc_y = inifoc_y + (endfoc_y - inifoc_y) * ratio
            camera(eye_x, eye_y, eye_z, foc_x, foc_y, foc_z, 0, 1, 0)
            yield
        
        for _ in xrange(self._fps * 2):
            yield
        self._fadeout = True
        cnt = self._fps * 6
        for _, ratio in range_curved(cnt):
            self._b_ratio = 1 - ratio
            yield

    @add_actor
    def textobject(self):
        cnt = 12
        for n in xrange(cnt):
            h = 350 - 40*self._b_ratio
            s = 30+70*(n/float(cnt))
            if self._fadeout:
                b = 100*self._b_ratio
            else:
                b = 30 + 70*self._b_ratio
            fill(color(h, s, b))
            text("Happy Birthday", width/2, height*0.66, n)
        return True