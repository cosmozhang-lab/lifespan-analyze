class Rect:
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
    @property
    def x(self):
        return self.left
    @property
    def y(self):
        return self.top
    @property
    def w(self):
        return self.width
    @property
    def h(self):
        return self.height
    @property
    def right(self):
        return self.left + self.width
    @property
    def bottom(self):
        return self.top + self.height
    
