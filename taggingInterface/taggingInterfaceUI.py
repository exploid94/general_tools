#!/usr/bin/env python
# ----------------------------------------------------------------------------#
# ------------------------------------------------------------------ HEADER --#
"""
:newField description: Description
:newField revisions: Revisions
:newField departments: Departments
:newField applications: Applications

:Authors:
    juphillips

:Organization:
    Reel FX Creative Studios

:Departments:
    rigging

:Description:
    Tool to be used for querying and manipulating both auto-generated and \
    custom rig tags within a rig during any stage of the rigging process.

============
Introduction
============

============
Standards
============

============
Notes
============

"""

# ----------------------------------------------------------------------------#
# ----------------------------------------------------------------- IMPORTS --#

# Built-in
import logging
from functools import partial
import webbrowser
import json
import os

# Third party
from maya import cmds
from maya.app.general.mayaMixin import (MayaQWidgetDockableMixin,
                                        MayaQDockWidget)

# Custom
from rig_tools.ui.Qt import QtCore, QtWidgets, QtGui
from rig_tools.ui.pyside import window, util, dialog


from rig_tools.tool.taggingInterface import taggingUtils
from rig_tools.tool.taggingInterface import tags

# ----------------------------------------------------------------------------#
# ----------------------------------------------------------------- GLOBALS --#
log = logging.getLogger(__name__)

TOOL_NAME = 'Tag Interface'
VERSION = '0.1.0'
LAST_UPDATE = 'January 25, 2023'
AUTHORS = ['juphillips']
ORGANIZATION = 'Reel FX Creative Studios'
DESCRIPTION = 'Tool to be used for querying and manipulating both auto-generated and ' \
              'custom attribute tags within an asset. Can also be used as a more ' \
              'general attribute lookup/creation tool.'
CONFLUENCE = 'https://confluence.reelfx.com/display/RIG/Tag+Interface'
CONFIG_DIR = os.path.join(os.environ['PKG_RIG_TOOLS'], 'tool', 'taggingInterface', 'configurations')

# ----------------------------------------------------------------------------#
# --------------------------------------------------------------- FUNCTIONS --#

def main(restore=True):
    tool = TagInterfaceUI.singleton()
    tool.show(dockable=True)

    if restore:
        tool.loadPreferences()
        tool.setWindowState()

    return tool

def saveJson(filepath, data):
    try:
        with open(filepath, 'w+') as outfile:
            json.dump(data, outfile)
        print ('File Saved:', filepath)
    except:
        raise
    return filepath

def loadJson(filepath):
    try:
        with open(filepath) as outfile:
            data = json.load(open(filepath))
    except:
        data = None
    return data

# ----------------------------------------------------------------------------#
# ----------------------------------------------------------------- Classes --#

class TagInterfaceUI(MayaQWidgetDockableMixin, window.Window):
    PREF_NAME = 'tag_interface_main_prefs'
    WINDOW_NAME = 'tag_interface'
    TITLE = 'Tag Interface'

    def __init__(self, *args, **kwargs):
        self.deleteInstances()

        super(TagInterfaceUI, self).__init__(*args, **kwargs)

        self.tagDicts = tags.STANDARD_TAGS_LIST

        self.initUI()

    def initUI(self):
        self.setObjectName(self.WINDOW_NAME)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.mainMenu = MainMenu(self.WINDOW_NAME, self)
        self.mainLayout.addWidget(self.mainMenu)

        self.filterWidget = FilterWidget(self)
        self.mainLayout.addWidget(self.filterWidget)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.mainLayout.addWidget(self.splitter)

        self.progress = 0
        self.progressBar = QtWidgets.QProgressBar()
        self.mainLayout.addWidget(self.progressBar)

        self.tagTree = AttributeTreeWidget(self)
        self.splitter.addWidget(self.tagTree)

        self.settingsWidget = SettingsWidget(self)
        self.splitter.addWidget(self.settingsWidget)

        self.splitter.setStretchFactor(0, 2)

    def resetProgressBar(self):
        self.progress = 0
        self.progressBar.reset()

    def initWindowState(self, *args, **kwargs):
        kwargs['x'] = self.windowPreferences.get('x', 800)
        kwargs['y'] = self.windowPreferences.get('y', 200)
        kwargs['width'] = self.windowPreferences.get('width', 800)
        kwargs['height'] = self.windowPreferences.get('height', 800)
        kwargs['liveSelection'] = self.windowPreferences.get('liveSelection', False)
        kwargs['terms'] = self.windowPreferences.get('terms', {})
        kwargs['searchExact'] = self.windowPreferences.get('searchExact', True)
        kwargs['searchUserDefined'] = self.windowPreferences.get('searchUserDefined', True)
        kwargs['searchScene'] = self.windowPreferences.get('searchScene', True)
        kwargs['searchSelected'] = self.windowPreferences.get('searchSelected', False)
        kwargs['searchHierarchy'] = self.windowPreferences.get('searchHierarchy', False)
        kwargs['searchNodeType'] = self.windowPreferences.get('searchNodeType', False)
        kwargs['nodeType'] = self.windowPreferences.get('nodeType', '')

    def getWindowState(self):
        """
        Override to accommodate MayaQWidgetDockableMixin
        """
        state = {}
        state['x'] = self.x()
        state['y'] = self.y()
        state['width'] = self.width()
        state['height'] = self.height()
        state['liveSelection'] = self.mainMenu.liveSelection.isChecked()
        state['terms'] = self.settingsWidget.termsList.getTermsState()
        state['searchExact'] = self.settingsWidget.searchExact.isChecked()
        state['searchUserDefined'] = self.settingsWidget.searchUserDefined.isChecked()
        state['searchScene'] = self.settingsWidget.searchScene.isChecked()
        state['searchSelected'] = self.settingsWidget.searchSelected.isChecked()
        state['searchHierarchy'] = self.settingsWidget.searchHierarchy.isChecked()
        state['searchNodeType'] = self.settingsWidget.searchNodeType.isChecked()
        state['nodeType'] = self.settingsWidget.nodeType.text()

        return state

    def setWindowState(self):
        prefs = self.windowPreferences
        self.settingsWidget.termsList.clear()
        for x in range(len(prefs['terms'])):
            itemName = prefs['terms'][str(x)]['itemName']
            isChecked = prefs['terms'][str(x)]['isChecked']
            self.settingsWidget.termsList.addTermAction(input=False, term=itemName, checkState=isChecked)
        self.mainMenu.liveSelection.setChecked(prefs['liveSelection'])
        self.settingsWidget.searchExact.setCheckState(prefs['searchExact'])
        self.settingsWidget.searchUserDefined.setCheckState(prefs['searchUserDefined'])
        self.settingsWidget.searchScene.setChecked(prefs['searchScene'])
        self.settingsWidget.searchSelected.setChecked(prefs['searchSelected'])
        self.settingsWidget.searchHierarchy.setCheckState(prefs['searchHierarchy'])
        self.settingsWidget.searchNodeType.setCheckState(prefs['searchNodeType'])
        self.settingsWidget.nodeType.setText(prefs['nodeType'])

    def show(self, *args, **kwargs):
        self.initWindowState(*args, **kwargs)
        super(TagInterfaceUI, self).show(*args, **kwargs)

    def showEvent(self, event):
        super(TagInterfaceUI, self).showEvent(event)

    def close(self):
        self.windowPreferences.update(self.getWindowState())
        self.savePreferences()
        self._removeWindow(self)
        super(TagInterfaceUI, self).close()

    def closeEvent(self, event):
        event.accept()
        self.close()

    def hide(self):
        self.windowPreferences.update(self.getWindowState())
        self.savePreferences()
        super(TagInterfaceUI, self).hide()

    def hideEvent(self, event):
        self.windowPreferences.update(self.getWindowState())
        self.savePreferences()
        super(TagInterfaceUI, self).hideEvent(event)

    def deleteInstances(self):
        mayaMainWindow = util.getMayaWindow()

        for child in mayaMainWindow.children():
            if type(child) == MayaQDockWidget:
                if child.widget().objectName() == self.WINDOW_NAME:
                    mayaMainWindow.removeDockWidget(child)
                    child.setParent(None)
                    child.deleteLater()

        self._deleteExistingWorkspaceControl()

    def _getWorkspaceControlName(self):
        return '{0}WorkspaceControl'.format(self.WINDOW_NAME)

    def _deleteExistingWorkspaceControl(self):
        workspaceName = self._getWorkspaceControlName()
        if cmds.workspaceControl(workspaceName, q=True, exists=True):
            cmds.workspaceControl(workspaceName, e=True, close=True)
            cmds.deleteUI(workspaceName, control=True)


class MainMenu(QtWidgets.QMenuBar):
    def __init__(self, WINDOW_NAME, parent):
        super(MainMenu, self).__init__(parent)
        self.parent = parent
        self.WINDOW_NAME = WINDOW_NAME
        util.setupQtUiElement(self, 'mainMenu', self.WINDOW_NAME)

        self.initMenuActions()
        self.fileMenu = self.addCustomMenu('File', self.fileActions)
        self.addCustomMenu('Load Default Config', self.defaultConfigActions, self.fileMenu)
        self.editMenu = self.addCustomMenu('Edit', self.editActions)
        self.helpMenu = self.addCustomMenu('Help', self.helpActions)

        self.setMaximumHeight(20)

    def addCustomMenu(self, menuName, actions=None, parentMenu=None):
        actions = actions or []

        if parentMenu is None:
            menu = self.addMenu(menuName)
        else:
            menu = parentMenu.addMenu(menuName)

        menuID = "{}Menu".format(menuName.replace(" ", ""))
        util.setupQtUiElement(menu, menuID, self.WINDOW_NAME)

        if parentMenu is not None:
            actions = [None] + actions

        for i, action in enumerate(actions):
            if isinstance(action, dict):
                actions[i] = self.addMenu(action['name'], action['items'], menu)

        util.addActions(menu, actions, self.WINDOW_NAME)

        return menu

    def initMenuActions(self):
        self.initFileActions()
        self.initEditActions()
        self.initHelpActions()

    def initFileActions(self):

        self.saveConfigAction = util.createAction(
            self,
            'Save Config',
            self.cb_saveConfig,
            tip='Saves the current preferences to file.'
        )

        self.openConfigAction = util.createAction(
            self,
            'Open Config',
            self.cb_openConfig,
            tip='Opens a saved preferences file.'
        )

        self.loadDefaultRigAction = util.createAction(
            self,
            'Rigging',
            partial(self.cb_loadDefaultConfig, 'rigging.config'),
            tip='Loads the default rigging configuration.'
        )

        self.defaultConfigActions = [
            self.loadDefaultRigAction,
        ]

        self.fileActions = [
            self.saveConfigAction,
            self.openConfigAction
        ]

    def initEditActions(self):

        self.liveSelection = util.createAction(
            self,
            'Live Selection',
            tip='Selects the object in the scene when you select object or attr in the UI.',
            checkable=True
        )

        self.loggingAction = util.createAction(
            self,
            'Logging',
            tip='Sets logging to the Preferred setting.'
        )

        self.loggingInfoAction = util.createAction(
            self,
            'Info',
            tip='Sets logging to the Info setting.'
        )

        self.loggingDebugAction = util.createAction(
            self,
            'Debug',
            tip='Sets logging to the Debug setting.'
        )

        self.loggingWarningAction = util.createAction(
            self,
            'Warning',
            tip='Sets logging to the Warning setting.'
        )

        self.editActions = [
            self.liveSelection
        ]

    def initHelpActions(self):

        self.confluenceAction = util.createAction(
            self,
            'Confluence',
            self.cb_confluence,
            tip='Open the confluence page for this tool.'
        )

        self.aboutAction = util.createAction(
            self,
            'About',
            self.cb_about,
            tip='Open about dialog for this tool.'
        )

        self.helpActions = [
            self.confluenceAction,
            self.aboutAction
        ]

    @QtCore.Slot()
    def cb_saveConfig(self):
        state = self.parent.getWindowState()
        startingDir = '/resource_center/rigging/maya/tagging_interface/configs/'
        savePath = QtWidgets.QFileDialog.getSaveFileName(self.parent,
                                                         'Save Config',
                                                         startingDir,
                                                         "Config Files (*.config)")[0]

        if savePath:
            saveJson(savePath, state)

    @QtCore.Slot()
    def cb_openConfig(self):
        startingDir = '/resource_center/rigging/maya/tagging_interface/configs/'
        openPath = QtWidgets.QFileDialog.getOpenFileName(self.parent,
                                                         'Open Config',
                                                         startingDir,
                                                         "Config Files (*.config)")
        if openPath:
            data = loadJson(openPath[0])
            prefs = self.parent.windowPreferences
            try:
                self.parent.windowPreferences = data
                self.parent.setWindowState()
            except:
                self.parent.windowPreferences = prefs
                self.parent.setWindowState()

    @QtCore.Slot()
    def cb_loadDefaultConfig(self, filename):
        filepath = str(os.path.join(CONFIG_DIR, filename))
        if os.path.exists(filepath):
            data = loadJson(filepath)
            prefs = self.parent.windowPreferences
            try:
                self.parent.windowPreferences = data
                self.parent.setWindowState()
            except:
                self.parent.windowPreferences = prefs
                self.parent.setWindowState()
        else:
            log.error('Filepath does not exist: %s', filepath)

    @QtCore.Slot()
    def cb_setLogging(self):
        pass

    @QtCore.Slot()
    def cb_confluence(self):
        webbrowser.open(CONFLUENCE)

    @QtCore.Slot()
    def cb_about(self):
        self.toolName = TOOL_NAME
        self.version = VERSION
        self.authors = ', '.join(AUTHORS)
        self.organization = ORGANIZATION
        self.description = DESCRIPTION

        self.aboutMessage = 'Tool Name: {}\n\n' \
                            'Version: {}\n\n' \
                            'Authors: {}\n\n' \
                            'Organization: {}\n\n' \
                            'Description: {}'.format(self.toolName,
                                                  self.version,
                                                  self.authors,
                                                  self.organization,
                                                  self.description)

        dialog.showMessage(self.aboutMessage, title='Tag Interface About')


class AttributeTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent):
        super(AttributeTreeWidget, self).__init__(parent)

        self.setFont(QtGui.QFont("Helvetica [Cronyx]", 10))

        self.setColumnCount(3)
        self.setHeaderLabels(['Name',
                              'Value',
                              'Attribute Type',
                              'Association'])
        self.setSortingEnabled(True)

        self.parent = parent

        self.progressBar = self.parent.progressBar
        self.progress = self.parent.progress

        self.topLevelItems = []
        self.objectTypes = {}
        self.objDict = {}

        # these lists are for populating the filter comboboxes
        self.attrNames = []
        self.attrTypes = []
        self.associations = []

        self.filterList = []
        self.filterObjNameList = []
        self.filterObjTypeList = []
        self.filterAttrNameList = []
        self.filterAttrTypeList = []
        self.filterAssociationList = []

        self.itemSelectionChanged.connect(self.selectObjectInScene)
        self.itemClicked.connect(self.selectObjectInScene)

        self.setColumnWidth(0, 300)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._showContextMenu)

    def _showContextMenu(self, position):
        menu = QtWidgets.QMenu(self)
        menu.addAction('Expand All', self.expandAll)
        menu.addAction('Collapse All', self.collapseAll)
        menu.addSeparator()
        menu.addAction('Copy Object Name', partial(self.copyObjectName, position))

        menu.exec_(self.mapToGlobal(position))

    @QtCore.Slot()
    def copyObjectName(self, position):
        item = self.itemAt(position)
        if item:
            item = self.getTopLevelItem(item)
            cb = QtWidgets.QApplication.clipboard()
            cb.setText(item.text(0))

    @QtCore.Slot()
    def populate(self):
        self.clear()

        self.topLevelItems = []
        self.objectTypes = {}

        self.settings = self.parent.settingsWidget

        exact = self.settings.searchExact.isChecked()
        ud = self.settings.searchUserDefined.isChecked()
        selected = self.settings.searchSelected.isChecked()
        dag = self.settings.searchHierarchy.isChecked()
        terms = self.parent.settingsWidget.termsList.getTerms()
        searchNodeType = self.parent.settingsWidget.searchNodeType.isChecked()
        if searchNodeType:
            nodeType = self.parent.settingsWidget.nodeType.text()
        else:
            nodeType = None

        self.objDict = taggingUtils.searchWithTerms(nodeType=nodeType,
                                                    terms=terms,
                                                    userDefined=ud,
                                                    searchExact=exact,
                                                    selection=selected,
                                                    dagObjects=dag,
                                                    progressBar=self.progressBar)

        try:
            x = (1.0/len(self.objDict)) * 50.0
        except:
            x = 100.0

        self.progress = 50.0
        self.progressBar.setValue(self.progress)

        for obj in self.objDict:
            top = self.addTopTreeItem(obj)
            for attr in self.objDict[obj]:
                self.addSubTreeItem(top,
                                    self.objDict[obj][attr]['name'],
                                    self.objDict[obj][attr]['value'],
                                    self.objDict[obj][attr]['type'],
                                    self.objDict[obj][attr]['association'],
                                    self.objDict[obj][attr]['description'])
            self.progress += x
            self.progressBar.setValue(self.progress)

        self.progressBar.setValue(100.0)

    def addTopTreeItem(self, name):
        item = QtWidgets.QTreeWidgetItem()

        item.setText(0, name)
        sizeHint = QtCore.QSize(250, 30)
        item.setSizeHint(0, sizeHint)

        self.addTopLevelItem(item)

        self.topLevelItems.append(item)
        self.filterList.append(name)

        self.objectTypes[name] = cmds.nodeType(name)

        return item

    def addSubTreeItem(self, top, name, value, attrType, association, description):
        item = QtWidgets.QTreeWidgetItem()

        valueDesc = 'The value or connections for tag: "{}"'.format(name)
        typeDesc = 'The attribute type for the tag: "{}".'.format(name)
        assocDesc = 'The tool or process associated with tag: "{}".'.format(name)

        item.setText(0, name)
        item.setText(1, value)
        item.setText(2, attrType)
        item.setText(3, association)
        item.setToolTip(0, description)
        item.setToolTip(1, valueDesc)
        item.setToolTip(2, typeDesc)
        item.setToolTip(3, assocDesc)

        top.addChild(item)

        # these lists are used for populating the filter comboboxes
        if name not in self.attrNames:
            self.attrNames.append(name)
        if attrType not in self.attrTypes:
            self.attrTypes.append(attrType)
        if association not in self.associations:
            self.associations.append(association)

        return item

    @QtCore.Slot()
    def selectObjectInScene(self):
        if self.parent.mainMenu.liveSelection.isChecked():
            current = self.currentItem()
            item = self.getTopLevelItem(current)
            obj_name = item.text(0)
            cmds.select(obj_name)

    def isTopLevelItem(self, item):
        if item.parent():
            return False
        else:
            return True

    def getTopLevelItem(self, item):
        if self.isTopLevelItem(item):
            return item
        else:
            return item.parent()

    def getSubTreeItem(self):
        pass

    def getSubTreeName(self, item):
        return item.text(0)

    def getSubTreeValue(self, item):
        return item.text(1)

    def getSubTreeType(self, item):
        return item.text(2)

    def getSubTreeAssociation(self, item):
        return item.text(3)

    def subTreeNameLookup(self, topLevelItem, name):
        resultList = []
        for index in range(topLevelItem.childCount()):
            if name in self.getSubTreeName(topLevelItem.child(index)):
                resultList.append(topLevelItem.child(index))
        return resultList

    def subTreeTypeLookup(self, topLevelItem, type):
        resultList = []
        for index in range(topLevelItem.childCount()):
            if type in self.getSubTreeType(topLevelItem.child(index)):
                resultList.append(topLevelItem.child(index))
        return resultList

    def subTreeAssociationLookup(self, topLevelItem, assoc):
        resultList = []
        for index in range(topLevelItem.childCount()):
            if assoc in self.getSubTreeAssociation(topLevelItem.child(index)):
                resultList.append(topLevelItem.child(index))
        return resultList

    @QtCore.Slot()
    def _filterObjectName(self):
        self.filterObjNameList = []
        name = self.parent.filterWidget.filterObjectName.text()

        if '*' in name:
            flags = (QtCore.Qt.MatchFlag.MatchWildcard | QtCore.Qt.MatchFlag.MatchCaseSensitive)
        else:
            flags = (QtCore.Qt.MatchFlag.MatchContains | QtCore.Qt.MatchFlag.MatchCaseSensitive)

        if name:
            for item in self.findItems(name, flags, 0):
                if self.isTopLevelItem(item):
                    self.filterObjNameList.append(item.text(0))
        else:
            for item in self.topLevelItems:
                if not item.text(0) in self.filterObjNameList:
                    self.filterObjNameList.append(item.text(0))

    @QtCore.Slot()
    def _filterObjectType(self):
        self.filterObjTypeList = []
        combobox = self.parent.filterWidget.filterObjectType
        if combobox.currentIndex() == 0:
            for item in self.topLevelItems:
                self.filterObjTypeList.append(item.text(0))
        else:
            for item in self.topLevelItems:
                if combobox.currentText() == self.objectTypes[item.text(0)]:
                    self.filterObjTypeList.append(item.text(0))
                else:
                    if item.text(0) in self.filterObjTypeList:
                        self.filterObjTypeList.remove(item.text(0))

    @QtCore.Slot()
    def _filterAttrName(self):
        self.filterAttrNameList = []
        combobox = self.parent.filterWidget.filterAttrName
        if combobox.currentIndex() == 0:
            for item in self.topLevelItems:
                self.filterAttrNameList.append(item.text(0))
        else:
            for item in self.topLevelItems:
                itemName = item.text(0)
                if self.subTreeNameLookup(item, combobox.currentText()):
                    if itemName not in self.filterAttrNameList:
                        self.filterAttrNameList.append(itemName)
                else:
                    if itemName in self.filterAttrNameList:
                        self.filterAttrNameList.remove(itemName)

    @QtCore.Slot()
    def _filterAttrType(self):
        self.filterAttrTypeList = []
        combobox = self.parent.filterWidget.filterAttrType
        if combobox.currentIndex() == 0:
            for item in self.topLevelItems:
                self.filterAttrTypeList.append(item.text(0))
        else:
            for item in self.topLevelItems:
                itemName = item.text(0)
                if self.subTreeTypeLookup(item, combobox.currentText()):
                    if itemName not in self.filterAttrTypeList:
                        self.filterAttrTypeList.append(itemName)
                else:
                    if itemName in self.filterAttrTypeList:
                        self.filterAttrTypeList.remove(itemName)

    @QtCore.Slot()
    def _filterAssociation(self):
        self.filterAssociationList = []
        combobox = self.parent.filterWidget.filterAssociation
        if combobox.currentIndex() == 0:
            for item in self.topLevelItems:
                self.filterAssociationList.append(item.text(0))
        else:
            for item in self.topLevelItems:
                itemName = item.text(0)
                if self.subTreeAssociationLookup(item, combobox.currentText()):
                    if itemName not in self.filterAssociationList:
                        self.filterAssociationList.append(itemName)
                else:
                    if itemName in self.filterAssociationList:
                        self.filterAssociationList.remove(itemName)

    def applyFilters(self):
        if self.parent.filterWidget.state:
            for item in self.topLevelItems:
                item.setHidden(True)
            self._filterObjectName()
            self._filterObjectType()
            self._filterAttrName()
            self._filterAttrType()
            self._filterAssociation()
            self._updateFilterList()
        else:
            for item in self.topLevelItems:
                item.setHidden(False)

    def _updateFilterList(self):
        self.filterList = []
        for item in self.topLevelItems:
            name = item.text(0)
            if name in self.filterObjNameList:
                if name in self.filterObjTypeList:
                    if name in self.filterAttrNameList:
                        if name in self.filterAttrTypeList:
                            if name in self.filterAssociationList:
                                self.filterList.append(name)
                                item.setHidden(False)


class FilterWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(FilterWidget, self).__init__(parent)

        self.parent = parent

        self.state = False

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)

        self.initUI()

        self.setMaximumHeight(80)

    def initUI(self):
        self.filterGroupBox = QtWidgets.QGroupBox("Search Filter")
        self.filterGroupBox.setFont(QtGui.QFont("Helvetica [Cronyx]", 12))
        self.filterLayout = QtWidgets.QGridLayout()
        self.filterGroupBox.setLayout(self.filterLayout)
        self.mainLayout.addWidget(self.filterGroupBox)

        self.filterLayout.setColumnStretch(0, 1)
        self.filterLayout.setColumnStretch(1, 1)
        self.filterLayout.setColumnStretch(2, 1)
        self.filterLayout.setColumnStretch(3, 1)
        self.filterLayout.setColumnStretch(4, 1)

        self.filterGroupBox.setCheckable(True)
        self.filterGroupBox.setChecked(False)
        self.filterGroupBox.clicked.connect(self._enableSwitch)

        self.filterObjectName = QtWidgets.QLineEdit()
        self.filterLayout.addWidget(self.filterObjectName, 0, 0, 1, 1)

        self.filterObjectType = QtWidgets.QComboBox()
        self.filterLayout.addWidget(self.filterObjectType, 0, 1, 1, 1)

        self.filterAttrName = QtWidgets.QComboBox()
        self.filterLayout.addWidget(self.filterAttrName, 0, 2, 1, 1)

        self.filterAttrType = QtWidgets.QComboBox()
        self.filterLayout.addWidget(self.filterAttrType, 0, 3, 1, 1)

        self.filterAssociation = QtWidgets.QComboBox()
        self.filterLayout.addWidget(self.filterAssociation, 0, 4, 1, 1)

    @QtCore.Slot()
    def _enableSwitch(self):
        self.state = self.filterGroupBox.isChecked()
        self.filterObjectName.setEnabled(self.state)
        self.filterObjectType.setEnabled(self.state)
        self.filterAttrName.setEnabled(self.state)
        self.filterAttrType.setEnabled(self.state)
        self.filterAssociation.setEnabled(self.state)

        self.filterObjectName.textChanged.connect(self.parent.tagTree.applyFilters)
        self.filterObjectType.currentIndexChanged.connect(self.parent.tagTree.applyFilters)
        self.filterAttrName.currentIndexChanged.connect(self.parent.tagTree.applyFilters)
        self.filterAttrType.currentIndexChanged.connect(self.parent.tagTree.applyFilters)
        self.filterAssociation.currentIndexChanged.connect(self.parent.tagTree.applyFilters)

        self.parent.tagTree.applyFilters()

    @QtCore.Slot()
    def populateFilters(self):
        self._populateObjectTypes()
        self._populateAttrNames()
        self._populateAttrTypes()
        self._populateAssociations()

    def _populateObjectTypes(self):
        self.filterObjectType.clear()
        self.filterObjectType.addItem("<Obj Types>")
        nodeTypes = []
        objectTypes = self.parent.tagTree.objectTypes
        for obj in objectTypes:
            if objectTypes[obj] not in nodeTypes:
                nodeTypes.append(objectTypes[obj])
                self.filterObjectType.addItem(objectTypes[obj])

    def _populateAttrNames(self):
        self.filterAttrName.clear()
        self.filterAttrName.addItem("<Attr Names>")
        names = self.parent.tagTree.attrNames
        self.filterAttrName.addItems(names)

    def _populateAttrTypes(self):
        self.filterAttrType.clear()
        self.filterAttrType.addItem("<Attr Types>")
        types = self.parent.tagTree.attrTypes
        self.filterAttrType.addItems(types)

    def _populateAssociations(self):
        self.filterAssociation.clear()
        self.filterAssociation.addItem("<Associations>")
        associations = self.parent.tagTree.associations
        self.filterAssociation.addItems(associations)


class SettingsWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(SettingsWidget, self).__init__(parent)

        self.parent = parent

        self.initUI()

    def initUI(self):
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.initTermsUI()
        self.initSearchPrefsUI()

        self.searchButton = QtWidgets.QPushButton("Search")
        self.mainLayout.addWidget(self.searchButton)
        self.searchButton.clicked.connect(self.parent.tagTree.populate)
        self.searchButton.clicked.connect(self.parent.filterWidget.populateFilters)

    def initTermsUI(self):
        self.termsGroupBox = QtWidgets.QGroupBox("Search Tags")
        self.termsGroupBox.setFont(QtGui.QFont("Helvetica [Cronyx]", 12))
        self.termsLayout = QtWidgets.QGridLayout()
        self.termsGroupBox.setLayout(self.termsLayout)
        self.mainLayout.addWidget(self.termsGroupBox)

        self.termsList = TermsWidget(self)
        self.termsLayout.addWidget(self.termsList, 0, 0, 1, 2)

        self.addTerm = QtWidgets.QPushButton("+")
        self.removeTerm = QtWidgets.QPushButton("-")
        self.termsLayout.addWidget(self.addTerm, 1, 0, 1, 1)
        self.termsLayout.addWidget(self.removeTerm, 1, 1, 1, 1)

        self.addTerm.clicked.connect(self.termsList.addTermAction)
        self.removeTerm.clicked.connect(self.termsList.removeTermAction)

        self.termsList.resetPreDefinedTerms()

    def initSearchPrefsUI(self):
        self.searchGroupBox = QtWidgets.QGroupBox("Search Settings")
        self.searchGroupBox.setFont(QtGui.QFont("Helvetica [Cronyx]", 12))
        self.searchLayout = QtWidgets.QGridLayout()
        self.searchGroupBox.setLayout(self.searchLayout)
        self.mainLayout.addWidget(self.searchGroupBox)

        self.searchExact = QtWidgets.QCheckBox("Search Exact Tags")
        #self.searchLayout.addWidget(self.searchExact, 0, 0, 1, 1)
        self.searchExact.setCheckState(QtCore.Qt.Checked)
        self.searchExact.setDisabled(True)

        self.searchUserDefined = QtWidgets.QCheckBox("Only User Defined")
        self.searchLayout.addWidget(self.searchUserDefined, 1, 0, 1, 1)
        self.searchExact.setCheckState(QtCore.Qt.Checked)
        self.searchUserDefined.setCheckState(QtCore.Qt.Checked)

        self.searchScene = QtWidgets.QRadioButton("Scene")
        self.searchScene.setChecked(True)
        self.searchSelected = QtWidgets.QRadioButton("Selected")
        self.searchHierarchy = QtWidgets.QCheckBox("Hierarchy")
        self.searchLayout.addWidget(self.searchScene, 2, 0, 1, 1)
        self.searchLayout.addWidget(self.searchSelected, 2, 1, 1, 1)
        self.searchLayout.addWidget(self.searchHierarchy, 2, 2, 1, 1)
        self.searchScene.toggled.connect(self._searchSelectedSwitch)
        self.searchHierarchy.setEnabled(False)

        self.searchNodeType = QtWidgets.QCheckBox("Only Node Type")
        self.searchNodeType.stateChanged.connect(self._searchNodeTypeSwitch)
        self.searchLayout.addWidget(self.searchNodeType, 3, 0, 1, 1)

        self.nodeType = QtWidgets.QLineEdit()
        self.searchLayout.addWidget(self.nodeType, 3, 1, 1, 2)
        self.nodeType.setEnabled(False)

    @QtCore.Slot()
    def _searchSelectedSwitch(self):
        if self.searchSelected.isChecked():
            self.searchHierarchy.setEnabled(True)
        else:
            self.searchHierarchy.setEnabled(False)

    @QtCore.Slot()
    def _searchNodeTypeSwitch(self):
        if self.searchNodeType.isChecked():
            self.nodeType.setEnabled(True)
        else:
            self.nodeType.setEnabled(False)


class TermsWidget(QtWidgets.QListWidget):
    def __init__(self, parent):
        super(TermsWidget, self).__init__(parent)

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._showContextMenu)

    def _showContextMenu(self, position):
        menu = QtWidgets.QMenu(self)
        menu.addAction("Check Selected", partial(self.checkSelectedTerms, True))
        menu.addAction("Uncheck Selected", partial(self.checkSelectedTerms, False))
        menu.addAction("Check All", partial(self.checkAllTerms, True))
        menu.addAction("Uncheck All", partial(self.checkAllTerms, False))
        menu.addAction("Add New Term", self.addTermAction)
        menu.addAction("Remove Selected Terms", self.removeTermAction)
        menu.addAction("Reset Pre-Defined Terms", self.resetPreDefinedTerms)

        menu.exec_(self.mapToGlobal(position))

    def getItemFromTerm(self, term):
        items = self.findItems(term, QtCore.Qt.MatchExactly | QtCore.Qt.MatchCaseSensitive)
        if items:
            return items[0]

    def getTerms(self, unchecked=False):
        terms = []
        for x in range(self.count()):
            if unchecked:
                terms.append(self.item(x).text())
            elif self.item(x).checkState() == QtCore.Qt.Checked:
                terms.append(self.item(x).text())
        return terms

    def getTermsState(self):
        terms = {}
        for x in range(self.count()):
            termAttr = {}
            termAttr['itemName'] = self.item(x).text()
            termAttr['isChecked'] = self.isItemChecked(self.item(x))
            terms[str(x)] = termAttr
        return terms

    def checkAllTerms(self, state=True):
        for x in range(self.count()):
            if state:
                self.item(x).setCheckState(QtCore.Qt.Checked)
            else:
                self.item(x).setCheckState(QtCore.Qt.Unchecked)

    def checkSelectedTerms(self, state=True):
        for item in self.selectedItems():
            if state:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

    def checkItem(self, item, state=True):
        if state:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)

    def isTermInList(self, term):
        if self.findItems(term, QtCore.Qt.MatchExactly | QtCore.Qt.MatchCaseSensitive):
            return True
        else:
            return False

    def isItemChecked(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            return True
        else:
            return False

    @QtCore.Slot()
    def addTermAction(self, input=True, term='', checkState=True, index=None):
        if input:
            term = dialog.getInput("Add a new term?")
        if term:
            if not self.isTermInList(term):
                item = QtWidgets.QListWidgetItem(term)
                item.setFont(QtGui.QFont("Helvetica [Cronyx]", 12))
                if checkState:
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
                if index:
                    self.insertItem(index, item)
                else:
                    self.addItem(item)

    @QtCore.Slot()
    def removeTermAction(self):
        for item in self.selectedItems():
            row = self.row(item)
            self.takeItem(row)

    @QtCore.Slot()
    def resetPreDefinedTerms(self):
        for term in taggingUtils.getStandardTags():
            if not self.isTermInList(term):
                self.addTermAction(input=False, term=term)


#==============================================================================
# Standalone
#==============================================================================
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = TagInterfaceUI()
    win.show()
    app.exec_()
