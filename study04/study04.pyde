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

def initial_actor(f):
    if not _ins.isgeneratorfunction(f):
        raise 'actor function must be generator function'
    setattr(f, _ATTR_INITIAL_ACTOR, True)
    return f

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
        for name, attr in _ins.getmembers(self):
            if hasattr(attr, _ATTR_INITIAL_ACTOR) and _ins.isgeneratorfunction(attr):
                self._acts.append(attr())
        return self
        
    def add_actor(self, gen):
        self._acts.append(gen)
        
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

SIZE_PARAMS = (600, 400, P3D)

@setup_controller
class Controller(BaseController):

    def mysetup(self):
        size(600, 400, P3D)
        blendMode(REPLACE)
        colorMode(RGB)
        textFont(createFont("Edwardian Script ITC", 90))
        textMode(SHAPE)
        textAlign(CENTER, CENTER)

    def pre_draw(self):
        background(0)

    def put_text(self):
        cnt = 15
        for n in xrange(cnt):
            fill(color(50+n*(150/cnt), 0, 30))
            text("Happy Birthday", width/2, height*0.66, n)

    @initial_actor
    def action(self):
        cnt = 60
        for n in xrange(cnt):
            camera(0+(width/cnt)*n, height*0.9, 80, 250, 200, 0, 0, 1, 0)
            self.put_text()
            yield