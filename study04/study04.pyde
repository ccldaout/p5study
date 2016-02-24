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

def movement_curve(x):
    x = 2*x - 1
    return 0.5 - x * (x*x - 3) / 4

def range_curved(ini, end, n, curve=movement_curve):
    s = end - ini
    for i in xrange(n+1):
        x = float(i)/n
        y = slice_curve(x)
        yield ini + s * y

SIZE_PARAMS = (600, 400, P3D)

@setup_controller
class Controller(BaseController):

    def mysetup(self):
        blendMode(REPLACE)
        colorMode(HSB, 360, 100, 100)
        textFont(createFont("Edwardian Script ITC", 90))
        textMode(SHAPE)
        textAlign(CENTER, CENTER)

    def pre_draw(self):
        background(0)

    @add_actor
    def camera(self):
        foc_x, foc_y, foc_z = width/2, height/2, 0
        eye_y = height * 0.9
        eye_z = 80

        cnt = 60
        for eye_x in range_curved(0, width, cnt):
            camera(eye_x, eye_y, eye_z, width/2, height/2, 0, 0, 1, 0)
            yield

        cnt = 30
        for ratio in range_curved(0, 1, cnt):
            eye_x = width * (1 - 0.5 * ratio)
            eye_y = height*0.9 * (1 - ratio)
            camera(eye_x, eye_y, eye_z, width/2, height/2, 0, 0, 1, 0)
            yield

    @add_actor
    def textobject(self):
        cnt = 15
        for n in xrange(cnt):
            fill(color(350, 65+30*(n/float(cnt)), 80))
            text("Happy Birthday", width/2, height*0.66, n)