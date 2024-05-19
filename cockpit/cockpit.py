from PyQt6.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow, QGridLayout, QDockWidget, QListWidget)
from PyQt6.QtGui import QImage, QPixmap, QPainter
from PyQt6.QtCore import Qt, QSize, QRect, pyqtSignal, pyqtSlot
from PyQt6 import QtWidgets, uic
import sys
import csv

from news.news_feed import NewsFeed

class MainWindow(QMainWindow):
    news_signal = pyqtSignal(dict, name="news_signal")
    def __init__(self):
        super().__init__()
        self.initUI()
        self.news_signal.connect(self.newsSlot)

    @staticmethod
    def _createPixmap(path):
        image = QImage()
        image.load(path, "WEBP")
        dim = 50
        pixmap = QPixmap(dim, dim)
        painter = QPainter(pixmap)
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawRect(-1, -1, dim+1, dim+1)
        if image.size().width() == 0:
            painter.end()
            return pixmap
        new_height = int(image.size().height()*dim/image.size().width())
        pad = (dim - new_height) // 2
        painter.drawImage(QRect(0, pad, dim, new_height), image, QRect(0, 0, image.size().width(), image.size().height()), Qt.ImageConversionFlag.ColorOnly)
        painter.end()
        return pixmap
        # pixmap.convertFromImage(image)
        # pixmap = pixmap.scaled(QSize(50, 50), Qt.AspectRatioMode.KeepAspectRatio)

    @pyqtSlot(dict)
    def newsSlot(self, keyword_bins):
        for keyword_iterable in keyword_bins:
            entries = keyword_bins[keyword_iterable]
            for entry in entries.values():
                self.news_list.addItem(entry['title'])

    def initUI(self):
        self.dock_widget = QDockWidget("S&P 500", self)
        self.setCentralWidget(self.dock_widget)
        self.scroll = QScrollArea(self.dock_widget)             # Scroll Area which contains the widgets, set as the centralWidget
        self.dock_widget.setWidget(self.scroll)
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.grid = QGridLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.grid.setHorizontalSpacing(14)
        base_thum_path = '/home/z640/Downloads/S&P 500 Stocks List of Companies_files/'
        r = 0
        headers = None
        with open('/home/z640/code/scratch/sAp.csv') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if r == 0:
                    headers = row
                    r += 1
                    continue
                c = 0
                label = QLabel()
                pixmap = MainWindow._createPixmap(base_thum_path + row[-2].strip())
                label.setPixmap(pixmap)
                self.grid.addWidget(label, r, c, Qt.AlignmentFlag.AlignLeft)
                c += 1
                for info in row[:2]:
                    label2 = QLabel(info)
                    self.grid.addWidget(label2, r, c, Qt.AlignmentFlag.AlignLeft)
                    c += 1

                # ticker = row[0]
                self.grid.setColumnStretch(2, 10)
                tooltip = ""
                for i in range(0, len(row)-2):
                    tooltip += headers[i] + ": " + row[i] + "\n"
                label.setToolTip(tooltip)
                r += 1
        self.widget.setLayout(self.grid)

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setGeometry(600, 100, 1000, 900)
        self.setWindowTitle('Scroll Area Demonstration')
        self.show()

        widget2 = QDockWidget("News", self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, widget2)
        self.news_list = QListWidget(widget2)
        widget2.setWidget(self.news_list)
        
        def callback(keyword_bins):
            self.news_signal.emit(keyword_bins)
        NewsFeed.get(callback)
    @staticmethod
    def start():
        app = QtWidgets.QApplication(sys.argv)
        main = MainWindow()
        sys.exit(app.exec())