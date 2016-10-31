from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os, os.path, sys
import lamp_gis
import lamp_gis_dialog

class MapExplorer(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("LampGis Standalone")
        self.resize(800, 400)
        self.toolBar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)

        icon = QIcon("icon.png")
        self.actionLaunchLampGis = QAction(icon, "LampGis", self)
        self.toolBar.addAction(self.actionLaunchLampGis)
        self.connect(self.actionLaunchLampGis, SIGNAL("triggered()"), self.launchLampGis)

    def launchLampGis(self):
        self.dlg = lamp_gis_dialog.LampGisDialog()
        self.dlg.show()


QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX_PATH'], True)
qgs = QgsApplication([], True)

qgs.initQgis()

window = MapExplorer()
window.show()
window.raise_()
qgs.exec_()
qgs.deleteLater()

qgs.exitQgis()