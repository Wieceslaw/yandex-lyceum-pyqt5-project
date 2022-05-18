import sys
import csv
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QPushButton, QLineEdit, QFileDialog, QColorDialog
from PyQt5.QtGui import QPainter, QColor
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from util.object import Object
from util.scaling import scale


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.fps = 60
        self.delay = round(1000 / self.fps)
        self.width = 1600
        self.height = 900
        self.object_dialog = uic.loadUi('ui/object.ui')
        self.object_dialog.pushButton.clicked.connect(self.change_object)
        self.setGeometry(100, 100, self.width, self.height)
        self.setWindowTitle('planets')
        fname = QFileDialog.getOpenFileName(self, 'Выбрать таблицу', '')[0]
        self.file_name = fname
        self.initUI()

    def initUI(self):
        self.fone_color = QColor(255, 255, 255)
        self.timer_on = False
        self.draw_names = True
        self.draw_lines = True
        self.draw_imp = True
        self.draw_tr = True
        self.central_object_nomber = 0

        self.smx = 0
        self.smy = 0
        self.mdx = 0
        self.mdy = 0
        self.mmx = 0
        self.mmy = 0
        self.x1 = 0
        self.y1 = 0
        self.coeff = 1
        self.c = 1

        self.px = 0
        self.py = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.paint)

        self.btn1 = QPushButton('Отображать имена', self)
        self.btn1.resize(120, 45)
        self.btn1.move(10, 60)
        self.btn1.clicked.connect(self.dr_nm)

        self.btn2 = QPushButton('Отображать линии', self)
        self.btn2.resize(120, 45)
        self.btn2.move(10, 110)
        self.btn2.clicked.connect(self.dr_ln)

        self.btn6 = QPushButton('Отобразить\nимпульс тел', self)
        self.btn6.resize(120, 45)
        self.btn6.move(10, 160)
        self.btn6.clicked.connect(self.dr_im)

        self.btn7 = QPushButton('Отобразить\nтраекторию тел', self)
        self.btn7.resize(120, 45)
        self.btn7.move(10, 210)
        self.btn7.clicked.connect(self.dr_tr)

        self.btn3 = QPushButton('Выбрать файл\nдля запуска', self)
        self.btn3.resize(120, 45)
        self.btn3.move(10, 260)
        self.btn3.clicked.connect(self.choose_file)

        self.btn4 = QPushButton('Выбрать цвет\nфона', self)
        self.btn4.resize(120, 45)
        self.btn4.move(10, 310)
        self.btn4.clicked.connect(self.choose_color)

        self.btn5 = QPushButton('Пуск\nПауза', self)
        self.btn5.resize(120, 45)
        self.btn5.move(10, 10)
        self.btn5.clicked.connect(self.switch)

        data = []
        self.clicked = []
        # выгрузка данных из таблицы
        with open(self.file_name, encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
            for i in reader:
                a = []
                for j in i:
                    try:
                        a.append(float(i[j]))
                    except Exception:
                        a.append(i[j])
                data.append(a)
        self.objects = []
        # создание объектов
        for el in data:
            self.objects.append(Object(*el))
        self.labels = [QLabel(self) for _ in self.objects]
        for i, obj in zip(self.labels, self.objects):
            i.resize(200, 30)
            i.setText(obj.name)
            # cоздание изображений
            if obj.pict != 'None':
                obj.lbl = QLabel(self)
                obj.pix = QPixmap(obj.pict)
                obj.lbl.setScaledContents(True)
                obj.lbl.setPixmap(obj.pix)
        self.data = data

    def choose_file(self):
        # выбор файла для загрузки
        fname = QFileDialog.getOpenFileName(self, 'Выбрать таблицу', '')[0]
        if fname != '':
            self.file_name = fname
            for obj in self.objects:
                if obj.lbl != None:
                    obj.lbl.hide()
            for lbl in self.labels:
                lbl.hide()
            self.timer.stop()
            self.initUI()
            self.repaint()

    def choose_color(self):
        # выбор цвета фона
        color = QColorDialog.getColor()
        self.fone_color = color

    def dr_nm(self):
        # включение отображения имён
        if self.draw_names:
            for i in self.labels:
                i.hide()
            self.draw_names = False
        else:
            for i in self.labels:
                i.show()
            self.draw_names = True
        self.repaint()

    def dr_ln(self):
        # включение отображения линий
        if self.draw_lines:
            self.draw_lines = False
        else:
            self.draw_lines = True
        self.repaint()

    def dr_im(self):
        # включение отображения импульса
        if self.draw_imp:
            self.draw_imp = False
        else:
            self.draw_imp = True
        self.repaint()

    def dr_tr(self):
        # включение отображения траектории
        if self.draw_tr:
            self.draw_tr = False
        else:
            self.draw_tr = True
        self.repaint()

    def gravity(self):
        # просчитывание гравитационного влияния объектов друг на друга
        for object in self.objects:
            for obj in self.objects:
                if object != obj:
                    object.gravity(obj)
        self.px = round(sum([obj.vx * obj.m for obj in self.objects]))
        self.py = round(sum([obj.vy * obj.m for obj in self.objects]))
        # инициализация гравитационного влияния
        for object in self.objects:
            object.init()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def paint(self):
        if self.timer_on:
            self.gravity()
        self.repaint()

    def draw(self, qp):
        # рисование фона
        qp.setBrush(self.fone_color)
        qp.drawRect(0, 0, self.width, self.height)
        # рисование объектов
        self.clicked.clear()
        for object in self.objects:
            self.clicked.append(object.draw(qp, self.x1, self.y1, self.coeff, self.draw_tr))
        # опционально:
        # отображение названий
        if self.draw_names:
            for i, object in zip(self.labels, self.objects):
                i.setText(f'{object.name}')
                i.move(*scale(*object.get_cords(), self.x1, self.y1, self.coeff))
        # отображение линий
        if self.draw_lines:
            mx, my = self.objects[self.central_object_nomber].get_cords()
            for object in self.objects[1:]:
                qp.drawLine(*scale(mx, my, self.x1, self.y1, self.coeff),
                            *scale(object.x, object.y, self.x1, self.y1, self.coeff))
        # отображение импульса системы тел
        if self.draw_imp:
            b1 = scale(self.objects[0].x, self.objects[0].y, self.x1, self.y1, self.coeff)
            b2 = scale(self.objects[1].x, self.objects[1].y, self.x1, self.y1, self.coeff)
            px = (b1[0] + b2[0]) / 2
            py = (b1[1] + b2[1]) / 2
            qp.drawLine(int(px), int(py),
                        int(px + self.px * self.coeff), int(py + self.py * self.coeff))

    def switch(self):
        # пауза и пуск
        if not self.timer_on:
            self.timer.start(self.delay)
            self.timer_on = True
        else:
            self.timer_on = False
            self.timer.stop()

    def mousePressEvent(self, event):
        self.smx = event.x()
        self.smy = event.y()
        # отслеживание нажания на объект
        for x, y, r, obj in self.clicked:
            if x + r >= self.smx >= x and y + r >= self.smy >= y:
                self.current_obj = obj
                self.object_dialog.show()
                self.object_dialog.lineEdit.setText(obj.name)
                self.object_dialog.lineEdit_2.setText\
                    (' '.join(map(str, [int(obj.red), int(obj.green), int(obj.blue)])))
                self.object_dialog.lineEdit_3.setText(str(int(obj.r)))
                self.object_dialog.lineEdit_4.setText(str(int(obj.tail)))
                self.object_dialog.lineEdit_5.setText(str(int(obj.m)))
                self.object_dialog.label.setScaledContents(True)
                if obj.lbl != None:
                    self.object_dialog.label.setPixmap(obj.pix)
                else:
                    self.object_dialog.label.setText('Изображение отсутсвует')
                break

    def mouseReleaseEvent(self, event):
        self.mdx += event.x() - self.smx
        self.mdy += event.y() - self.smy
        self.x1 = self.mmx
        self.y1 = self.mmy
        self.repaint()

    def mouseMoveEvent(self, event):
        self.mmx = event.x() + self.mdx - self.smx
        self.mmy = event.y() + self.mdy - self.smy
        self.x1 = self.mmx
        self.y1 = self.mmy
        self.repaint()

    def wheelEvent(self, event):
        self.c += int(event.angleDelta().y() / 120)
        self.coeff = 1.5 ** (self.c / 4)
        self.repaint()

    def change_object(self):
        # изменение данных объекта из диалогового окна
        with open(self.file_name, 'w', newline='', encoding='utf8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow('id;x;y;vx;vy;m;r;red;green;blue;tail;name;pict'.split(';'))
            for el in self.data:
                if el[0] == self.current_obj.id:
                    el[5] = self.object_dialog.lineEdit_5.text()
                    el[6] = self.object_dialog.lineEdit_3.text()
                    el[7], el[8], el[9]  = list(self.object_dialog.lineEdit_2.text().split())
                    el[10] = self.object_dialog.lineEdit_4.text()
                    el[11] = self.object_dialog.lineEdit.text()
                writer.writerow(el)

        self.current_obj.name = self.object_dialog.lineEdit.text()
        self.current_obj.red, self.current_obj.green, self.current_obj.blue = list(map(int, self.object_dialog.lineEdit_2.text().split()))
        self.current_obj.r = int(self.object_dialog.lineEdit_3.text())
        self.current_obj.tail = int(self.object_dialog.lineEdit_4.text())
        self.current_obj.m = int(self.object_dialog.lineEdit_5.text())

        self.object_dialog.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())