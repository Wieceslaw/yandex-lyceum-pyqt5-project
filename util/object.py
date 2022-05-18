import math
from util.scaling import scale
from PyQt5.QtGui import QPainter, QColor


class Object:
    def __init__(self, id, x, y, vx, vy, m, r, red, green, blue, tail, name, pict):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.m = m
        self.r = r
        self.path = []
        self.red = red
        self.green = green
        self.blue = blue
        self.tail = tail
        self.name = name
        self.pict = pict
        self.lbl = None
        self.pix = None

    def gravity(self, other):
        if len(self.path) > self.tail:
            del self.path[0]
        self.path.append((self.x, self.y))
        d = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        a = other.m / (d ** 2)
        cos = (other.x - self.x) / d
        sin = (other.y - self.y) / d
        ax = a * cos
        ay = a * sin
        self.vx += ax
        self.vy += ay

    def init(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, qp, x, y, c, draw_tr):
        if self.pict == 'None':
            # выбор цвета
            qp.setBrush(QColor(self.red, self.green, self.blue))
            # рисованеи объекта
            qp.drawEllipse(self.x * c + x - self.r * c,
                           self.y * c + y - self.r * c,
                           2 * self.r * c,
                           2 * self.r * c)
        else:
            # передвижение изображения объекта
            self.lbl.show()
            self.lbl.move(self.x * c + x - self.r * c,
                          self.y * c + y - self.r * c)
            self.lbl.resize(2 * self.r * c,
                            2 * self.r * c)
        # рисование траектории
        if draw_tr:
            for i in range(len(self.path)):
                if i > 0:
                    qp.drawLine(*scale(self.path[i - 1][0], self.path[i - 1][1], x, y, c),
                                *scale(self.path[i][0], self.path[i][1], x, y, c))

        return (int(self.x * c + x - self.r * c),
                int(self.y * c + y - self.r * c),
                int(2 * self.r * c),
                self)

    def get_cords(self):
        return self.x, self.y