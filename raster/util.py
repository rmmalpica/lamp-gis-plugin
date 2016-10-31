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
from qgis.core import QgsRectangle


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

    def __init__(self, qgsRasterLayer):
        """Constructor.

        :param width: Block width.
        :param height: Block height
        :param extent: Block coordinates extent
        """

        self.qgsRasterLayer = qgsRasterLayer


    def splitIntoBlocks(self):

        MAX_WIDTH = 1000
        dataProvider = self.qgsRasterLayer.dataProvider()

        width = self.qgsRasterLayer.width()
        height = self.qgsRasterLayer.height()
        xRes = self.qgsRasterLayer.rasterUnitsPerPixelX()
        yRes = self.qgsRasterLayer.rasterUnitsPerPixelY()
        extent = dataProvider.extent()

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

                extent = QgsRectangle(xmin, ymin, xmax, ymax)

                rasterBlock = LmpgRasterBlock(blocksWidth[x], blocksHeight[y], extent)
                row.append(rasterBlock)

            blocks.append(row)

        return blocks