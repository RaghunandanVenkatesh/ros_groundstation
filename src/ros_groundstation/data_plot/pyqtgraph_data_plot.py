from python_qt_binding.QtCore import Slot, Qt, qVersion, qWarning, Signal
from python_qt_binding.QtGui import QColor
from python_qt_binding.QtWidgets import QVBoxLayout, QWidget

if qVersion().startswith('5.'):
    try:
        from pkg_resources import parse_version
    except:
        import re

        def parse_version(s):
            return [int(x) for x in re.sub(r'(\.0+)*$', '', s).split('.')]

    from pyqtgraph import __version__ as pyqtgraph_version
    if parse_version(pyqtgraph_version) < parse_version('0.10.0'):
        raise ImportError('A newer PyQtGraph version is required (at least 0.10 for Qt 5)')

from pyqtgraph import PlotWidget, mkPen, mkBrush
import numpy


class PyQtGraphDataPlot(QWidget):

    limits_changed = Signal()

    def __init__(self, parent=None):
        super(PyQtGraphDataPlot, self).__init__(parent)
        self._plot_widget = PlotWidget()
        self._plot_widget.getPlotItem().addLegend()
        self._plot_widget.setBackground((255, 255, 255))
        self._plot_widget.setXRange(0, 10, padding=0)
        vbox = QVBoxLayout()
        vbox.addWidget(self._plot_widget)
        self.setLayout(vbox)
        self._plot_widget.getPlotItem().sigRangeChanged.connect(self.limits_changed)

        self._curves = {}
        self._current_vline = None

    def add_curve(self, curve_id, curve_name, curve_color=QColor(Qt.blue), markers_on=False):
        #print 'activated.' # ---------------------------------------------
        pen = mkPen(curve_color, width=1)
        symbol = "o"
        symbolPen = mkPen(QColor(Qt.black))
        symbolBrush = mkBrush(curve_color)
        # this adds the item to the plot and legend
        if markers_on:
            plot = self._plot_widget.plot(name=curve_name, pen=pen, symbol=symbol, symbolPen=symbolPen, symbolBrush=symbolBrush, symbolSize=4)
        else:
            plot = self._plot_widget.plot(name=curve_name, pen=pen)
        self._curves[curve_id] = plot
        #self._update_legend()# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        #print self._curves # ----------------------------------------

    def remove_curve(self, curve_id):
        curve_id = str(curve_id)
        if curve_id in self._curves:
            self._plot_widget.removeItem(self._curves[curve_id])
            del self._curves[curve_id]
            self._update_legend()

    def _update_legend(self):
        # clear and rebuild legend (there is no remove item method for the legend...)
        self._plot_widget.clear()
        self._plot_widget.getPlotItem().legend.items = []
        for curve in list(self._curves.values()):
            #print 'added curve'
            self._plot_widget.addItem(curve)
        if self._current_vline:
            self._plot_widget.addItem(self._current_vline)

    def redraw(self):
        pass

    def set_values(self, curve_id, data_x, data_y):
        curve = self._curves[curve_id]
        curve.setData(data_x, data_y)

    def vline(self, x, color):
        if self._current_vline:
            self._plot_widget.removeItem(self._current_vline)
        self._current_vline = self._plot_widget.addLine(x=x, pen=color)

    def set_xlim(self, limits):
        # TODO: this doesn't seem to handle fast updates well
        self._plot_widget.setXRange(limits[0], limits[1], padding=0)

    def set_ylim(self, limits):
        self._plot_widget.setYRange(limits[0], limits[1], padding=0)

    def get_xlim(self):
        x_range, _ = self._plot_widget.viewRange()
        return x_range

    def get_ylim(self):
        _, y_range = self._plot_widget.viewRange()
        return y_range
