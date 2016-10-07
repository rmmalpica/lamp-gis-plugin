# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LampGis
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QSize

from PyQt4.QtGui import QAction, QIcon
from qgis.gui import QgsMessageBar
# Initialize Qt resources from file resources.py 
import resources
# Import the code for the dialog
from lamp_gis_dialog import LampGisDialog
import os.path
import mysql.connector
from mysql.connector import errorcode
from PyQt4.Qt import QColor

class LampGis:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LampGis_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LampGisDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&LAMP GIS')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'LampGis')
        self.toolbar.setObjectName(u'LampGis')
        
        #self.dlg.connectButton.clicked.connect(self.connectButtonClicked_handler)
        self.dlg.saveButton.clicked.connect(self.saveButtonClicked_handler)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LampGis', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/LampGis/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'LAMPGIS'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&LAMP GIS'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

#     def connectButtonClicked_handler(self):
#         config = {
#             'user': self.dlg.userText.text(),
#             'password': self.dlg.passwordText.text(),
#             'host': self.dlg.hostText.text(),
#             'database': self.dlg.databaseText.text(),
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
        
        selectedLayerIndex = self.dlg.layersComboBox.currentIndex()
        selectedLayer = self.layers[selectedLayerIndex]
        self.dlg.infoText.setPlainText(selectedLayer.extent().toString())
        self.dlg.infoText.appendPlainText(selectedLayer.metadata())
        self.dlg.infoText.appendPlainText(selectedLayer.renderer().type())
        self.dlg.infoText.appendPlainText("Width: {}".format(selectedLayer.width()))
        self.dlg.infoText.appendPlainText("Height: {}".format(selectedLayer.height()))
        self.dlg.infoText.appendPlainText("providerType: {}".format(selectedLayer.providerType()))
        
        self.dlg.infoText.appendPlainText("----------------------")
        
        dataProvider = selectedLayer.dataProvider()        
        self.dlg.infoText.appendPlainText("dataProvider.bandOffset: {}".format(dataProvider.bandOffset(1)))
        self.dlg.infoText.appendPlainText("dataProvider.bandScale: {}".format(dataProvider.bandScale(1)))
        self.dlg.infoText.appendPlainText("dataProvider.bandOffset: {}".format(dataProvider.bandOffset(2)))
        self.dlg.infoText.appendPlainText("dataProvider.bandScale: {}".format(dataProvider.bandScale(2)))
        self.dlg.infoText.appendPlainText("dataProvider.bandOffset: {}".format(dataProvider.bandOffset(3)))
        self.dlg.infoText.appendPlainText("dataProvider.bandScale: {}".format(dataProvider.bandScale(3)))
        
        block1 = dataProvider.block(1, selectedLayer.extent(), selectedLayer.width(), selectedLayer.height())
        color = block1.color(1,1)
        self.dlg.infoText.appendPlainText("block1.color: {}".format(color))
        #self.dlg.infoText.appendPlainText("block1.bits: {}".format(block1.bits()))
        
        self.dlg.infoText.appendPlainText("----------------------")
        
        if selectedLayer.isValid():   

            image = selectedLayer.previewAsImage(QSize(selectedLayer.width()/10, selectedLayer.height()/10), 
                                             QColor(0,0,0,0))
        else:
            self.iface.messageBar().pushMessage("Error", "Raster not loaded", 
                                               level=QgsMessageBar.CRITICAL)
            
        self.dlg.infoText.appendPlainText("Byte Count: {}".format(image.byteCount()))
        self.dlg.infoText.appendPlainText("Bytes per line: {}".format(image.bytesPerLine()))
        self.dlg.infoText.appendPlainText("Depth: {}".format(image.depth()))
        self.dlg.infoText.appendPlainText("dotsPerMeterX: {}".format(image.dotsPerMeterX()))
        self.dlg.infoText.appendPlainText("dotsPerMeterY: {}".format(image.dotsPerMeterY()))
        
        #image.save("image.tiff", "TIFF", 50)
        

    def run(self):
                        
        self.layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in self.layers:
            layer_list.append(layer.name())
 
        self.dlg.layersComboBox.clear()
        self.dlg.layersComboBox.addItems(layer_list)
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
