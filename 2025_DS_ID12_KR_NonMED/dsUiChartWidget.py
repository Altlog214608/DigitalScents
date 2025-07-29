from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter #, QPalette, QImage
from PySide6.QtWidgets import (QWidget, QSizePolicy, QHBoxLayout)
from PySide6.QtCharts import (QChart, QChartView,
                              QLineSeries, QPieSeries, 
                              # QScatterSeries, QSplineSeries, QStackedBarSeries, 
                              QValueAxis)

import dsText

# https://doc.qt.io/qtforpython-6/tutorials/datavisualize/plot_datapoints.html

# 파이 차트 위젯
class scentPieChartWidget(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)

        # Pie Chart
        self.pie_chart = QChart()
        self.pie_chart_view = QChartView(self.pie_chart)
        # Size
        size = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        size.setHorizontalStretch(1)
        size.setVerticalStretch(1)
        self.pie_chart_view.setSizePolicy(size)
        self.pie_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing) # Anti-aliasing
        # Layout
        self.hbl = QHBoxLayout()
        self.hbl.addWidget(self.pie_chart_view)
        self.setLayout(self.hbl)

        # Init Series
        self.pie_series = QPieSeries(self.pie_chart)
        self.pie_series.setPieSize(1)
        
        # Legend 데이터 표시 (밑에 1줄 주석 해제하면 나타난다.)
        self.pie_chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom) # Legend alignment
        self.pie_chart.legend().hide() # 숨김
        self.pie_chart.addSeries(self.pie_series) # 시리즈는 생성시에만 Add
        # self.applyPieChart(10, 0) # 초기화

    def applyPieChart(self, data_incorrect, data_correct): # 메뉴 -> TDI 화면 파이차트
        # Clear
        self.pie_series.clear()
        self.pie_series.append(dsText.resultText['index_correct'], data_correct)
        self.pie_series.append(dsText.resultText['index_incorrect'], data_incorrect)
        self.setThemePieChart()

    def apply_pie_chart(self, data_incorrect, data_correct): # 검사 -> 파이차트: 개발 필요
        # Clear
        self.pie_series.clear()
        self.pie_series.append(dsText.resultText['index_correct'], data_correct)
        self.pie_series.append(dsText.resultText['index_incorrect'], data_incorrect)
        self.setThemePieChart()

    def setThemePieChart(self):
        # Legend 데이터 표시
        # self.pie_chart.legend().setAlignment(Qt.AlignmentFlag.AlignTop) # Legend alignment
        # self.pie_chart.legend().hide()
        # Anti-aliasing
        # self.pie_chart_view.setRenderHint(QPainter.Antialiasing)
        # Slice
        self.slice_1 = self.pie_series.slices()[0]
        self.slice_1.setBrush(Qt.GlobalColor.green)
        # self.slice_1.setLabelVisible(True)
        # self.slice_1.setExploded()
        # self.slice_1.setExplodeDistanceFactor(0.02)
        self.slice_2 = self.pie_series.slices()[1]
        self.slice_2.setBrush(Qt.GlobalColor.red)
        # self.slice_2.setLabelVisible(False)
        # self.slice_2.setExploded()

# 라인 차트 위젯
class scentLineChartWidget(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        # Line Chart
        self.line_chart = QChart()
        self.line_chart_view = QChartView(self.line_chart)
        self.line_chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.hbl = QHBoxLayout()
        
        # Legend 데이터 표시 숨김
        self.line_chart.legend().hide()
        # self.line_chart.legend().setAlignment(Qt.AlignmentFlag.AlignTop) # Legend alignment
        # self.line_chart.addSeries(self.line_series) # 시리즈는 생성시에만 Add

        self.hbl.addWidget(self.line_chart_view)
        self.setLayout(self.hbl)

    def applyLineChart(self, x_data, y_data): # 메뉴 -> TDI 화면 라인차트
        # print(x_data)
        # print(y_data)
        # Clear
        self.line_chart.removeAllSeries()
        # self.line_series.clear()
        series = QLineSeries(self.line_chart)

        series.setColor(QColor("red"))
        series.setPointsVisible(True)

        for i in range(0, len(x_data)):
            series.append(x_data[i]+1, y_data[i])
            
        self.line_chart.addSeries(series)
        
        # Setting X-axis
        self.axis_x = QValueAxis()
        # self.axis_x.setTitleText("회차")
        self.line_chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(self.axis_x)
        # # Setting Y-axis
        self.axis_y = QValueAxis()
        # self.axis_y.setTitleText("역치")
        self.line_chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(self.axis_y)

        self.line_chart.createDefaultAxes()
        axis_x = self.line_chart.axes(Qt.Horizontal)[0] # 첫번째 수평축
        axis_x.setMin(1)
        axis_x.setMax(max([5, len(x_data)]))
        # axis_x.setRange(1, len(x_data))
        axis_x.setLabelFormat("%d")
        # axis_x.setTickCount(max([5, len(x_data)])) # 작은 화면에서 숫자가 ... 으로 표시되는 문제로 주석 처리
        axis_y = self.line_chart.axes(Qt.Vertical)[0] # 첫번째 수직축
        axis_y.setMin(1)
        axis_y.setMax(12)
        # axis_y.setRange(0, 12)
        axis_y.setLabelFormat("%d")
        # axis_y.setTickCount(12) # 작은 화면에서 숫자가 ... 으로 표시되는 문제로 주석 처리

    def apply_line_chart(self, x_data, y_data): # 검사 -> 라인차트: 개발 필요
        # Clear
        self.line_chart.removeAllSeries()
        series = QLineSeries(self.line_chart)

        series.setColor(QColor("red"))
        series.setPointsVisible(True)

        for i in range(0, len(x_data)):
            series.append(x_data[i]+1, y_data[i])
            
        self.line_chart.addSeries(series)
        
        # Setting X-axis
        self.axis_x = QValueAxis()
        # self.axis_x.setTitleText("회차")
        self.line_chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(self.axis_x)
        # # Setting Y-axis
        self.axis_y = QValueAxis()
        # self.axis_y.setTitleText("역치")
        self.line_chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(self.axis_y)

        self.line_chart.createDefaultAxes()
        axis_x = self.line_chart.axes(Qt.Horizontal)[0] # 첫번째 수평축
        axis_x.setMin(1)
        axis_x.setMax(max([5, len(x_data)]))
        # axis_x.setRange(1, len(x_data))
        axis_x.setLabelFormat("%d")
        axis_x.setTickCount(max([5, len(x_data)]))
        axis_y = self.line_chart.axes(Qt.Vertical)[0] # 첫번째 수직축
        axis_y.setMin(1)
        axis_y.setMax(12)
        # axis_y.setRange(0, 12)
        axis_y.setLabelFormat("%d")
        axis_y.setTickCount(12)

    def apply_line_4_chart(self, x1, y1, x2, y2, x3, y3, x4, y4):
        # Clear
        self.line_chart.removeAllSeries()
        series1 = QLineSeries(self.line_chart)
        series2 = QLineSeries(self.line_chart)
        series3 = QLineSeries(self.line_chart)
        series4 = QLineSeries(self.line_chart)

        series1.setColor(QColor("red"))
        series1.setPointsVisible(True)
        series2.setColor(QColor("orange"))
        series2.setPointsVisible(True)
        series3.setColor(QColor("brown"))
        series3.setPointsVisible(True)
        series4.setColor(QColor("green"))
        series4.setPointsVisible(True)

        for i1 in range(0, len(x1)):
            series1.append(x1[i1], y1[i1])
        for i2 in range(0, len(x2)):
            series2.append(x2[i2], y2[i2])
        for i3 in range(0, len(x3)):
            series3.append(x3[i3], y3[i3])
        for i4 in range(0, len(x4)):
            series4.append(x4[i4], y4[i4])
            
        self.line_chart.addSeries(series1)
        self.line_chart.addSeries(series2)
        self.line_chart.addSeries(series3)
        self.line_chart.addSeries(series4)
        
        # # Setting X-axis
        # self.axis_x = QValueAxis()
        # # self.axis_x.setTitleText("회차")
        # self.line_chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        # series1.attachAxis(self.axis_x)
        # series2.attachAxis(self.axis_x)
        # series3.attachAxis(self.axis_x)
        # series4.attachAxis(self.axis_x)
        # # Setting Y-axis
        # self.axis_y = QValueAxis()
        # # self.axis_y.setTitleText("역치")
        # self.line_chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        # series1.attachAxis(self.axis_y)
        # series2.attachAxis(self.axis_y)
        # series3.attachAxis(self.axis_y)
        # series4.attachAxis(self.axis_y)

        self.line_chart.createDefaultAxes()
        axis_x = self.line_chart.axes(Qt.Horizontal)[0] # 첫번째 수평축
        # axis_x.setMin(1)
        # axis_x.setMax(max([5, len(x1), len(x2), len(x3), len(x4)]))
        # # axis_x.setRange(1, len(x_data))
        axis_x.setLabelFormat("%d")
        # axis_x.setTickCount(5) #max([5, len(x1), len(x2), len(x3), len(x4)]))
        axis_y = self.line_chart.axes(Qt.Vertical)[0] # 첫번째 수직축
        axis_y.setMin(0)
        axis_y.setMax(10)
        # # axis_y.setRange(0, 12)
        axis_y.setLabelFormat("%d")
        # axis_y.setTickCount(10)