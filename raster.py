# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LampGis
                                 A QGIS plugin
 Plugin to import / export from a LAMP GIS source
                              -------------------
        begin                : 2016-10-24
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
from PyQt4.Qt import QImage, qRgba, QPoint
from qgis.core import QgsRectangle, QgsRaster
import os.path
import logging
import gzip
import requests




class LmpgRasterBlock:
    """Class to store width, height and Rectangle of a raster."""

    def __init__(self, width, height, extent):
        """Constructor.

        :param width: Block width.
        :param height: Block height
        :param extent: Block coordinates extent
        """
        
        self.width = width
        self.height = height
        self.extent = extent


class LmpgRaster:
    """Class to store width, height and Rectangle of a raster."""

    def __init__(self, qgsRasterLayer, layerName):
        """Constructor.

        :param qgsRasterLayer: QgsRasterLayer object.
        :param layerName: Name given to the raster
        """

        self.qgsRasterLayer = qgsRasterLayer
        self.name = layerName
        self.tmpPath = os.path.dirname(__file__)+"/tmp/"


    def _splitIntoBlocks(self, width, height, extent):

        MAX_WIDTH = 1000

        xRes = self.qgsRasterLayer.rasterUnitsPerPixelX()
        yRes = self.qgsRasterLayer.rasterUnitsPerPixelY()

        blocks = []
        MAX_HEIGHT = (float(height) / float(width)) * MAX_WIDTH

        if width <= MAX_WIDTH:
            rasterBlock = LmpgRasterBlock(self.qgsRasterLayer.width(), self.qgsRasterLayer.height(),
                                          self.qgsRasterLayer.extent())
            row = []
            row.append(rasterBlock)
            blocks.append(row)
            return blocks

        blocksWidth = []
        blocksHeight = []
        xBlocks = 1
        yBlocks = 1
        blockWidth = width
        blockHeight = height

        while blockWidth >= MAX_WIDTH:
            xBlocks += 1
            blockWidth = width / xBlocks

        for x in range(xBlocks):
            blocksWidth.append(blockWidth)

        MAX_HEIGHT = (float(height) / float(width)) * float(blockWidth)

        while blockHeight >= MAX_HEIGHT:
            yBlocks += 1
            blockHeight = height / yBlocks

        for y in range(yBlocks):
            blocksHeight.append(blockHeight)

        modWidth = width % xBlocks
        modHeight = height % yBlocks

        x = 0
        while modWidth > 0:
            blocksWidth[x] += 1
            modWidth -= 1
            x += 2
            if x > (len(blocksWidth) - 1):
                x = 1

        y = 0
        while modHeight > 0:
            blocksHeight[y] += 1
            modHeight -= 1
            y += 2
            if y > (len(blocksHeight) - 1):
                y = 1

        for y in range(len(blocksHeight)):
            row = []
            for x in range(len(blocksWidth)):
                xmin = extent.xMinimum() + (x * blocksWidth[x] * xRes)
                ymin = extent.yMinimum() + (y * blocksHeight[y] * yRes)
                xmax = extent.xMinimum() + ((x + 1) * blocksWidth[x] * xRes)
                ymax = extent.yMinimum() + ((y + 1) * blocksHeight[y] * yRes)

                blockExtent = QgsRectangle(xmin, ymin, xmax, ymax)

                rasterBlock = LmpgRasterBlock(blocksWidth[x], blocksHeight[y], blockExtent)
                row.append(rasterBlock)

            blocks.append(row)

        return blocks

    def _getRasterData(self):

        data = dict()
        data["name"] = self.name
        data["metadata"] = self.qgsRasterLayer.metadata()
        data["xmin"] = self.qgsRasterLayer.extent().xMinimum()
        data["ymin"] = self.qgsRasterLayer.extent().yMinimum()
        data["xmax"] = self.qgsRasterLayer.extent().xMaximum()
        data["ymax"] = self.qgsRasterLayer.extent().yMaximum()
        data["width"] = self.qgsRasterLayer.width()
        data["height"] = self.qgsRasterLayer.height()
        data["bandCount"] = self.qgsRasterLayer.bandCount()
        data["rasterUnitsPerPixelX"] = self.qgsRasterLayer.rasterUnitsPerPixelX()
        data["rasterUnitsPerPixelY"] = self.qgsRasterLayer.rasterUnitsPerPixelY()

        dataProvider = self.qgsRasterLayer.dataProvider()

        if dataProvider.srcHasNoDataValue(1):
            data["noDataValue"] = dataProvider.srcNoDataValue(1)
        else:
            data["noDataValue"] = ""

        statistics = dataProvider.bandStatistics(1)

        data["stat_max"] = statistics.maximumValue
        data["stat_min"] = statistics.minimumValue
        data["stat_mean"] = statistics.mean
        data["stat_std_dev"] = statistics.stdDev

        extent = dataProvider.extent()
        data["extent"] = extent.asWktPolygon()

        return data

    def _selectPyramids(self, pyramidList):

        for i in range(len(pyramidList)):

            pyramid = pyramidList[i]

            if not pyramid.exists and pyramid.xDim > 100:
                pyramid.build = True

    def _uploadBlocks(self, url, dataProvider, blocks, id, pyramidLevel=1):

        statistics = dataProvider.bandStatistics(1)

        for y in range(len(blocks)):
            row = blocks[y]
            for x in range(len(row)):
                rasterBlock = row[x]
                extent = rasterBlock.extent
                width = rasterBlock.width
                height = rasterBlock.height
                block = dataProvider.block(1, extent, width, height)

                blockData = dict()
                blockData["command"] = "add_raster_layer_block"
                blockData["id"] = id
                blockData["name"] = self.name
                blockData["xblock"] = x
                blockData["yblock"] = y
                blockData["width"] = block.width()
                blockData["height"] = block.height()
                blockData["xmin"] = extent.xMinimum()
                blockData["ymin"] = extent.yMinimum()
                blockData["xmax"] = extent.xMaximum()
                blockData["ymax"] = extent.yMaximum()
                blockData["extent"] = extent.asWktPolygon()
                blockData["level"] = pyramidLevel

                logging.info("block ({},{}) extent: ".format(x, y) + extent.toString())

                image = QImage(block.width(), block.height(), QImage.Format_ARGB32)
                file_gzip = gzip.open(self.tmpPath + "image{}_{}.gz".format(y, x), 'wb')
                valueString = ""

                for y2 in range(block.height()):
                    for x2 in range(block.width()):
                        value = block.value(y2, x2)
                        valueString += "{} ".format(value)
                        imageValue = (value - statistics.minimumValue) * (
                            255 / (statistics.maximumValue - statistics.minimumValue))

                        if imageValue >= 0 and imageValue < 256:
                            image.setPixel(QPoint(x2, y2),
                                           qRgba(int(imageValue), int(imageValue), int(imageValue), 255))
                        else:
                            image.setPixel(QPoint(x2, y2), qRgba(0, 0, 0, 0))
                            #                            message = "Excluded: {}".format(imageValue)
                            #                            logging.info(message)

                    valueString += "\n"

                saved = image.save(self.tmpPath + "image{}_{}.png".format(y, x), "PNG")
                file_gzip.write(valueString)
                file_gzip.close()

                files = {'dataFile': open(self.tmpPath + "image{}_{}.gz".format(y, x), 'rb')}
                files['imageFile'] = open(self.tmpPath + "image{}_{}.png".format(y, x), 'rb')
                r = requests.post(url, data=blockData, files=files)

                files['dataFile'].close()
                files['imageFile'].close()
                os.remove(self.tmpPath + "image{}_{}.png".format(y, x))
                os.remove(self.tmpPath + "image{}_{}.gz".format(y, x))


    def upload(self, url):

        dataProvider = self.qgsRasterLayer.dataProvider()
        width = self.qgsRasterLayer.width()
        height = self.qgsRasterLayer.height()
        extent = dataProvider.extent()
        blocks = self._splitIntoBlocks(width, height, extent)
        pyramidList = dataProvider.buildPyramidList()

        data = self._getRasterData()
        data["command"] = "create_raster_layer"

        id = requests.post(url, data=data)

        self._uploadBlocks(url, dataProvider, blocks, id.content)

        if not dataProvider.hasPyramids():
            self._selectPyramids(pyramidList)
            dataProvider.buildPyramids(pyramidList, "AVERAGE")

        for i in range(len(pyramidList)):
            pyramid = pyramidList[i]
            blocks = self._splitIntoBlocks(pyramid.xDim, pyramid.yDim, dataProvider.extent())
            if pyramid.exists:
                self._uploadBlocks(url, dataProvider, blocks, id.content, pyramid.level)


