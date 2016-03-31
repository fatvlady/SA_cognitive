# coding: utf8


from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QPixmap, QImage

from graphviz import Digraph
from csv import reader

import os.path
import numpy as np

form_class, base_class = loadUiType(os.path.join(os.path.dirname(__file__), 'main_form.ui'))


class MainWindow(QDialog):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)
        self.ui = form_class()
        self.ui.setupUi(self)
        self.graph = Digraph(comment='Когнитивная карта', name='Cognitive map', format='png')
        self.labels = None
        self.matrix = None

    def load_labels(self, path):
        self.labels = list()
        with open(path, 'r') as label_file:
            csv_rdr = reader(label_file)
            header = next(csv_rdr)
            for row in csv_rdr:
                self.labels.append(row[0])

    def __fill_labels(self):
        if self.labels is not None and self.matrix is not None:
            self.labels.extend('add' + str(i) for i in range(0, max(self.matrix.shape[0] - len(self.labels), 0)))

    def load_matrix(self, path):
        self.matrix = np.load(path)

    @pyqtSlot(int)
    def pageChanged(self, page):
        if page == 1:
            self.render_graph()

    @pyqtSlot(QTableWidgetItem)
    def tableItemChanged(self, item):
        x = item.row()
        y = item.column()
        if str(self.matrix[x, y]) == item.data(0):
            return
        value = None
        try:
            value = np.float64(item.data(0))
            if not np.isfinite(value):
                raise ValueError('NaN')
            self.matrix[x, y] = value
        except ValueError:
            return
        finally:
            item.setData(0, str(self.matrix[x, y]))

    def render_table(self):
        if self.matrix is None or self.matrix.shape[0] != self.matrix.shape[1]:
            return
        if self.labels is None or len(self.labels) != self.matrix.shape[0]:
            return
        self.__fill_labels()
        self.ui.tableWidget.setRowCount(self.matrix.shape[0])
        self.ui.tableWidget.setColumnCount(self.matrix.shape[1])
        self.ui.tableWidget.setHorizontalHeaderLabels(self.labels)
        self.ui.tableWidget.setVerticalHeaderLabels(self.labels)
        for i in range(self.matrix.shape[0]):
            for j in range(self.matrix.shape[1]):
                self.ui.tableWidget.setItem(i, j, QTableWidgetItem(str(self.matrix[i, j])))

    def render_graph(self):
        if self.matrix is None or self.matrix.shape[0] != self.matrix.shape[1]:
            return
        if self.labels is None or len(self.labels) != self.matrix.shape[0]:
            return
        self.__fill_labels()
        cycles = find_cycles(self.matrix)
        self.graph = Digraph(comment='Когнитивная карта', name='Cognitive map', format='png')
        for i, label in enumerate(self.labels):
            self.graph.node(str(i), label, color='blue')
        size = len(self.labels)
        for i in range(size):
            for j in range(size):
                weight = self.matrix[i, j]
                if weight != 0:
                    self.graph.edge(str(i), str(j), label=str(weight),
                                    color='green' if weight > 0 else 'red', fontsize='10')
        img = QImage.fromData(self.graph.pipe(), "png")
        self.ui.graphView.setPixmap(QPixmap.fromImage(img))


def find_cycles(adj : np.array):
    assert adj.shape[0] == adj.shape[1]
    size = adj.shape[0]
    used = np.array([0]*size)
    cycles = list()
    def dfs(root, parent):
        used[root] = 1
        trace = list()
        for num, weight in enumerate(adj[root]):
            if num != parent and weight != 0:
                if used[num] == 0:
                    trace.extend(dfs(num, root))
                elif used[num] == 1:
                    trace.append([num])
                else:
                    continue
        used[root] = 2
        for path in trace:
            if path[0] == root:
                cycles.append(path)
                trace.remove(path)
            else:
                path.append(root)
        return trace
    dfs(0,-1)
    return cycles