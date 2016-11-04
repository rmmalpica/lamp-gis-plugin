# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LampGisDialogCtl
                                 A QGIS plugin
 Plugin to import / export from a LAMP GIS source
                             -------------------
        begin                : 2016-10-31
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Raúl Malpica
        email                : raul.malpica@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.Qt import QFileInfo
from PyQt4.QtGui import QFileDialog
from qgis.core import QgsMessageLog, QgsRasterLayer
from raster import LmpgRaster
import os.path
import logging


class LampGisDialogCtl():

    def __init__(self, gui, parent=None):
        """Constructor."""
        self.gui = gui
        self.parent = parent

        self.gui.layersComboBox.clear()

        if self.parent is not None:
            self.layers = self.parent.iface.legendInterface().layers()
            layer_list = []
            for layer in self.layers:
                layer_list.append(layer.name())

            self.gui.layersComboBox.addItems(layer_list)


    def findFileButtonClicked_handler(self):

        filename = QFileDialog.getOpenFileName(self.gui, "Select input raster ", "", '*.*')
        self.gui.fileNameText.setText(filename)
#     def connectButtonClicked_handler(self):
#         config = {
#             'user': self.gui.userText.text(),
#             'password': self.gui.passwordText.text(),
#             'host': self.gui.hostText.text(),
#             'database': self.gui.databaseText.text(),
#             'raise_on_warnings': True,
#             }
#
#         try:
#
#             self.cnx = mysql.connector.connect(**config)
#
#         except mysql.connector.Error as err:
#             if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#                 self.iface.messageBar().pushMessage("Error", "Something is wrong with your user name or password",
#                                                level=QgsMessageBar.CRITICAL)
#             elif err.errno == errorcode.ER_BAD_DB_ERROR:
#                 self.iface.messageBar().pushMessage("Error", "Database does not exist",
#                                                level=QgsMessageBar.CRITICAL)
#
#             else:
#                 self.iface.messageBar().pushMessage("Error", "Error: {}".format(err),
#                                                level=QgsMessageBar.CRITICAL)
#         else:
#             self.iface.messageBar().pushMessage("Info", "Connection Succeeded", level=QgsMessageBar.INFO)

    def saveButtonClicked_handler(self):

        selectedLayerName = ""

        if self.parent is not None:
            selectedLayerIndex = self.gui.layersComboBox.currentIndex()
            selectedLayer = self.layers[selectedLayerIndex]
            selectedLayerName = self.layers[selectedLayerIndex].name()
        else:
            fileName = self.gui.fileNameText.text()
            fileInfo = QFileInfo(fileName)
            baseName = fileInfo.baseName()
            selectedLayerName = baseName
            selectedLayer = QgsRasterLayer(fileName, baseName)


        self.gui.infoText.setPlainText(selectedLayer.extent().toString())
        # self.gui.infoText.appendPlainText(selectedLayer.metadata())
        self.gui.infoText.appendPlainText(selectedLayer.renderer().type())
        self.gui.infoText.appendPlainText("Width: {}".format(selectedLayer.width()))
        self.gui.infoText.appendPlainText("Height: {}".format(selectedLayer.height()))
        self.gui.infoText.appendPlainText("providerType: {}".format(selectedLayer.providerType()))
        self.gui.infoText.appendPlainText("bandCount: {}".format(selectedLayer.bandCount()))
        self.gui.infoText.appendPlainText("isSpatial: {}".format(selectedLayer.isSpatial()))
        self.gui.infoText.appendPlainText("rasterType: {}".format(selectedLayer.rasterType()))
        self.gui.infoText.appendPlainText("rasterUnitsPerPixelX: {}".format(selectedLayer.rasterUnitsPerPixelX()))
        self.gui.infoText.appendPlainText("rasterUnitsPerPixelY: {}".format(selectedLayer.rasterUnitsPerPixelY()))

        self.gui.infoText.appendPlainText("----------------------")

        dataProvider = selectedLayer.dataProvider()
        self.gui.infoText.appendPlainText("dataProvider.hasPyramids : {}".format(dataProvider.hasPyramids()))
        self.gui.infoText.appendPlainText("dataProvider.dataType: {}".format(dataProvider.dataType(1)))
        self.gui.infoText.appendPlainText("dataProvider.srcHasNoDataValue: {}".format(dataProvider.srcHasNoDataValue(1)))
        self.gui.infoText.appendPlainText("dataProvider.srcNoDataValue: {}".format(dataProvider.srcNoDataValue(1)))

        qlist = dataProvider.buildPyramidList()
        self.gui.infoText.appendPlainText("dataProvider.buildPyramidList: {}".format(len(qlist)))

        self.gui.infoText.appendPlainText("----------------------")
        crs = selectedLayer.crs()
        self.gui.infoText.appendPlainText("crs.authid : " + crs.authid())
        self.gui.infoText.appendPlainText("crs.description : " + crs.description())
        self.gui.infoText.appendPlainText("crs.geographicCRSAuthId : " + crs.geographicCRSAuthId())
        self.gui.infoText.appendPlainText("crs.mapUnits: {}".format(crs.mapUnits()))

        lmpgRaster = LmpgRaster(selectedLayer, selectedLayerName)
        lmpgRaster.upload("http://localhost:8080/LampGis/index.php")

        self.gui.infoText.appendPlainText("----------------------")
