# coding: utf8


from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QFileDialog, QAction, QErrorMessage, QTableWidgetItem
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QPixmap, QImage

from graphviz import Digraph
from csv import reader

import os.path
import numpy as np
from gui.read_data import read_data
from gui.error_message import error
from gui.tablewidget import tw

form_class, base_class = loadUiType(os.path.join(os.path.dirname(__file__), 'main_form.ui'))


class MainWindow(QDialog):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)


        self.ui = form_class()
        self.ui.setupUi(self)

        self.graph = Digraph(comment='Когнитивная карта', name='Cognitive map', format='png')
        self.labels = None
        self.matrix = None

        #set tableWidget
        self.tw = tw(self.ui.tw)
        #self.tw.verticalHeader().hide()
        #self.tw.setRowCount(0)
        #self.column_size = 50
        # for index, size in enumerate(column_size):
        #      self.ui.tw.setColumnWidth(index,size)
        # return

    @pyqtSlot()
    def saveImage(self):
        name = QFileDialog.getSaveFileName(self, "Save as", "", "PNG(*.png);; JPEG(*.jpg *.jpeg)")[0]
        if name != "":
            self.ui.graphView.grab().save(name)


    def load_labels(self, path):
        with open(path, 'r') as label_file:
            csv_rdr = reader(label_file)
            self.labels = list()
            header = next(csv_rdr)
            for row in csv_rdr:
                self.labels.append(row[0])

    def load_matrix(self, path):
        self.matrix = np.load(path)

    @pyqtSlot(int)
    def pageChanged(self, page):
        if page == 1:
            self.render_graph()

    def render_graph(self):
        if self.matrix is None or self.matrix.shape[0] != self.matrix.shape[1]:
            return
        if self.labels is None or len(self.labels) != self.matrix.shape[0]:
            return
        self.graph = Digraph(comment='Когнитивная карта', name='Cognitive map', format='png')
        for i, label in enumerate(self.labels):
            self.graph.node(str(i), label, color='blue')
        size = len(self.labels)
        for i in range(size):
            for j in range(size):
                weight = self.matrix[i, j]
                if weight != 0:
                    self.graph.edge(str(i), str(j), label=str(weight),
                                    color='green' if weight > 0 else 'red')
        graph = QImage.fromData(self.graph.pipe(), "png")
        self.ui.graphView.setPixmap(QPixmap.fromImage(graph))

    @pyqtSlot()
    def import_sheet(self):
        try:
            name = QFileDialog.getOpenFileName(self, "Open file", "", "Microsoft Excel(*.xlsx *.xls)")[0]
            matrix= np.array(read_data(name))
            if len(matrix) == 0 or len(matrix) != len(matrix[0]):
                raise Exception('Reformat matrix in file')
            self.tw.data = matrix
            self.tw.update_data()
        except Exception as e:
            error(e)

    @pyqtSlot()
    def addFactor(self):
        try:
            n = len(self.tw.data)
            matrix = np.zeros(shape = (n+1, n+1), dtype = float)
            matrix[:n, :n] = self.tw.data
            self.tw.data = matrix
            self.tw.update_data()
        except Exception as e:
            error(e)




