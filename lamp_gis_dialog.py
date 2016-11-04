# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LampGisDialog
                                 A QGIS plugin
 Plugin to import / export from a LAMP GIS source
                             -------------------
        begin                : 2016-09-12
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

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import SIGNAL
from lamp_gis_dialog_ctl import LampGisDialogCtl

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'lamp_gis_dialog_base.ui'))


class LampGisDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(LampGisDialog, self).__init__(None)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.ctl = LampGisDialogCtl(self, parent)

        #Connectors
        self.saveButton.clicked.connect(self.ctl.saveButtonClicked_handler)
        self.findFileButton.clicked.connect(self.ctl.findFileButtonClicked_handler)


