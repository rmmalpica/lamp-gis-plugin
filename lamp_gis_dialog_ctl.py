# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LampGisDialogCtl
                                 A QGIS plugin
 Plugin to import / export from a LAMP GIS source
                             -------------------
        begin                : 2016-10-31
        git sha              : $Format:%H$
        copyright            : (C) 2016 by RaÃºl Malpica
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

from PyQt4.Qt import QImage, qRgb, QPoint, QFileInfo
from PyQt4.QtGui import QFileDialog
from qgis.core import QgsMessageLog, QgsRasterLayer
from raster.util import LmpgRaster
import logging

class LampGisDialogCtl():
    def __init__(self, gui, parent=None):
        """Constructor."""
        self.gui = gui
        self.parent = parent

        self.initGui()

    def initGui(self):

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

        if self.parent is not None:
            selectedLayerIndex = self.gui.layersComboBox.currentIndex()
            selectedLayer = self.layers[selectedLayerIndex]
        else:
            fileName = self.gui.fileNameText.text()
            fileInfo = QFileInfo(fileName)
            baseName = fileInfo.baseName()
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

        lmpgRaster = LmpgRaster(selectedLayer)
        blocks = lmpgRaster.splitIntoBlocks()

        # if not dataProvider.hasStatistics(1):
        statistics = dataProvider.bandStatistics(1)

        # image = QImage(selectedLayer.width(), selectedLayer.height(), QImage.Format_ARGB32)

        count = 0
        countError = 0

        for y in range(len(blocks)):
            row = blocks[y]
            for x in range(len(row)):
                rasterBlock = row[x]
                extent = rasterBlock.extent
                width = rasterBlock.width
                height = rasterBlock.height
                block = dataProvider.block(1, extent, width, height)
                QgsMessageLog.logMessage("block extent: " + extent.toString(), "lamp-gis")
                image = QImage(block.width(), block.height(), QImage.Format_ARGB32)

                for y2 in range(block.height()):
                    for x2 in range(block.width()):
                        value = block.value(y2, x2)
                        imageValue = (value - statistics.minimumValue) * (
                            255 / (statistics.maximumValue - statistics.minimumValue))

                        if value == -999 or value == 0:
                            imageValue = 0
                        else:
                            message = "x: {}".format(x2) + " y: {}".format(y2) + " value: {}".format(
                                value) + " imageValue: {}".format(imageValue)
                            logging.info(message)

                        if imageValue > 0 and imageValue < 256:
                            count += 1
                            image.setPixel(QPoint(x2, y2), qRgb(int(imageValue), int(imageValue), int(imageValue)))
                        else:
                            image.setPixel(QPoint(x2, y2), qRgb(0, 0, 0))
                            countError += 1
                            message = "Excluded: {}".format(imageValue)
                            logging.info(message)

                saved = image.save("********************image{}_{}.png".format(y, x), "PNG")
                QgsMessageLog.logMessage("image_{}".format(y) + "{}".format(x) + " saved: {}".format(saved))

        self.gui.infoText.appendPlainText("----------------------")
        self.gui.infoText.appendPlainText("count: {}".format(count))
        self.gui.infoText.appendPlainText("countError: {}".format(countError))

    # rows = selectedLayer.height()
    # cols = selectedLayer.width()
    #
    # block = dataProvider.block(1, selectedLayer.extent(), selectedLayer.width(), selectedLayer.height())
    #
    # self.gui.infoText.appendPlainText("block is valid: {}".format(block.isValid()))
    #
    # for x2 in range(cols):
    #     for y2 in range(rows):
    #         value = block.value(y2, x2)
    #         #message = "x: {}".format(x2) + " y: {}".format(y2) + " value: {}".format(value)
    #         #logging.debug(message)
    #         imageValue = (value - statistics.minimumValue) * (255 / (statistics.maximumValue - statistics.minimumValue))
    #
    #         if value == -999 or value == 0:
    #             imageValue = 0
    #
    #         if imageValue > 0 and imageValue < 256:
    #             count += 1
    #             image.setPixel(QPoint(x2, y2), qRgb(int(imageValue), int(imageValue), int(imageValue)))
    #         else:
    #             image.setPixel(QPoint(x2, y2), qRgb(0, 0, 0))
    #             countError += 1
    #             message = "Excluded: {}".format(imageValue)
    #             logging.debug(message)
    #
    # saved = image.save("D:\\image.png", "PNG")
    # self.gui.infoText.appendPlainText("image saved: {}".format(saved))
