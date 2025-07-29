from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt

# PYSIDE_DESIGNER_PLUGINS
from PySide6.QtDesigner import QPyDesignerCustomWidgetCollection

class scentSlider(QSlider):
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            e.accept()
            x = e.pos().x()
            value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
            self.setValue(value)
        else:
            return super().mousePressEvent(self, e)

# Custome StyleSheets
# Progress bar
pb_blue_style = "QProgressBar {\
	                border: 2px solid rgba(77, 127, 243, 180);\
	                border-radius: 5px;\
	                text-align: center;\
	                background-color: rgba(77, 127, 243, 180);\
	                color: black;\
                }\
                QProgressBar::chunk {\
                    background-color: #AAD7DD;\
                }"
pb_red_style = "QProgressBar {\
	                border: 2px solid rgba(176, 91, 161, 180);\
	                border-radius: 5px;\
	                text-align: center;\
	                background-color: rgba(176, 91, 161, 180);\
	                color: black;\
                }\
                QProgressBar::chunk {\
                    background-color: #EB88DA;\
                }"