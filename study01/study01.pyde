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

@setup_controller(600, 400, P2D, save_fps=0.0)
class Controller(BaseController):

    def mysetup(self):
        pass

    def pre_draw(self):
        background(0)

    @add_actor
    def fog(self):
        yield
