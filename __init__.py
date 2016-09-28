# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LampGis
                                 A QGIS plugin
 Plugin to import / export from a LAMP GIS source
                             -------------------
        begin                : 2016-09-12
        copyright            : (C) 2016 by Raúl Malpica
        email                : raul.malpica@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load LampGis class from file LampGis.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .lamp_gis import LampGis
    return LampGis(iface)
