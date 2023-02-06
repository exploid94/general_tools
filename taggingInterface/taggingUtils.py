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
    custom tags within a maya file during any stage of the rigging process. \
    Alternatively, the user may use this tool as a maya attribute viewer.

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
import os
import datetime
import logging

# Third party
from maya import cmds

# Custom
from rig_tools.ui.pyside import dialog
import tags


# ----------------------------------------------------------------------------#
# ----------------------------------------------------------------- GLOBALS --#


log = logging.getLogger(__name__)

# ----------------------------------------------------------------------------#
# --------------------------------------------------------------- FUNCTIONS --#


def getStandardTags(validDicts=tags.STANDARD_TAGS_LIST):
    tagList = []
    for dictionary in validDicts:
        for tag in dictionary:
            if tag not in tagList:
                tagList.append(tag)
    return tagList


def searchWithTerms(terms=tags.COMMON_TERMS,
                    nodeType=None,
                    userDefined=True,
                    selection=False,
                    dagObjects=False,
                    searchExact=True,
                    progressBar=None):
    """Searches for nodes with attributes containing the terms.

    :parameters:
        terms : list
            The terms to look for within the user defined attributes.

        nodeType : str
            Maya node type to be used for listing objects in filter. Default: None

        userDefined : bool
            If True, the search will only look for user created attributes.

        selection : bool
            If True, the search will only find objects currently selected. Default: False

        dag : bool
            If True, the search will only find objects currently selected and it's children. Default: False

        searchExact : bool
            If True, then the search will only find items that match the exact text given.

        progressBar : QtWidgets.QProgressBar
            This will add progress to the progressBar starting from 0 and will max out at 50.

    :return: The tagged nodes with the given terms.
    :rtype: dict
    """

    def _updateAttrDataDict(dict, attr, obj):
        dict['name'] = attr
        dict['type'] = cmds.getAttr('{}.{}'.format(obj, attr), type=True)
        try:
            value = str(cmds.getAttr('{}.{}'.format(obj, attr)))
        except:
            try:
                value = str(cmds.listConnections('{}.{}'.format(obj, attr)))
            except:
                value = "HELP"
        dict['value'] = value
        dict['association'] = getTagAssociation(attr)
        dict['description'] = getTagDescription(attr)


    ### TODO need to move the searchExact outside the for loop and search \
    ### by cmds.ls("*.attr") for speed purposes but leaving it alone for now.
    obj_dict = {}

    if nodeType:
        obj_list = cmds.ls(type=nodeType, sl=selection, dag=dagObjects)
    else:
        obj_list = cmds.ls(sl=selection, dag=dagObjects)

    if progressBar:
        x = (1.0 / len(obj_list)) * 50.0

        progress = 0.0
        progressBar.setValue(progress)

    for obj in obj_list:
        attr_dict = {}
        attrs = cmds.listAttr(obj, ud=userDefined)
        if attrs:
            for attr in attrs:
                attr_data_dict = {}
                for term in terms:
                    if searchExact:
                        if term == attr and attr not in attr_dict:
                            _updateAttrDataDict(attr_data_dict, attr, obj)
                    else:
                        if term.lower() in attr.lower() and attr not in attr_dict:
                            _updateAttrDataDict(attr_data_dict, attr, obj)
                if attr_data_dict:
                    attr_dict[attr] = attr_data_dict
        if attr_dict:
            obj_dict[obj] = attr_dict

        if progressBar:
            progress += x
            progressBar.setValue(progress)

    return obj_dict


def createTagMetaData(node):
    """Creates the tags meta data attribute on specified node if it doesnt exist.

    :parameters:
        node : str
            The node to add the attribute to.

    :return: The tag meta data attribute
    :rtype: str
    """
    if hasTagMetaData(node):
        log.debug('%s attribute already exists on node %s', tags.TAGS_META_DATA_ATTR, node)
    else:
        cmds.addAttr(node, ln=tags.TAGS_META_DATA_ATTR, dt='string')
        cmds.setAttr('{}.{}'.format(node, tags.TAGS_META_DATA_ATTR), '{}', type='string', lock=True)
        log.debug('%s attribute created on node %s', tags.TAGS_META_DATA_ATTR, node)
        updateAllTagMetaData(node)
        log.debug('updated all meta data on node %s', node)
    return '{}.{}'.format(node, tags.TAGS_META_DATA_ATTR)


def deleteTagMetaData(node):
    """Deletes the tags meta data attribute on specified node if it exists.

        :parameters:
            node : str
                The node to remove the attribute from.
        """
    if hasTagMetaData(node):
        cmds.setAttr('{}.{}'.format(node, tags.TAGS_META_DATA_ATTR), lock=False)
        cmds.deleteAttr('{}.{}'.format(node, tags.TAGS_META_DATA_ATTR))
        log.debug('removed %s attribute on node %s', tags.TAGS_META_DATA_ATTR, node)
    else:
        log.debug('attribute %s doesnt exist on node %s', tags.TAGS_META_DATA_ATTR, node)


def resetTagMetaData(node):
    """Resets the tag meta data attr on a given node. Sets it to an empty dict.

    :parameters:
        node : str
            The node to reset the tag meta data attr on.
    """
    if hasTagMetaData(node):
        deleteTagMetaData(node)
        createTagMetaData(node)
        log.debug('reset the %s attribute on node %s', tags.TAGS_META_DATA_ATTR, node)


def hasTagMetaData(node):
    """Checks if the node has the tag meta data attribute.

    :parameters:
        node : str
            The node to check if it has the attr.

    :return: The state of whether the node has the attr or not.
    :rtype: bool
    """
    exists = cmds.attributeQuery(tags.TAGS_META_DATA_ATTR, n=node, exists=True)
    if not exists:
        log.warning('%s attribute does NOT exist for node %s', tags.TAGS_META_DATA_ATTR, node)
    return exists


def getTagMetaData(node):
    """Gets the tag meta data for the node as a dict.

    :parameters:
        node : str
            The node to get the attr from.

    :return: The value from the attr if it exists.
    :rtype: dict or None
    """
    if hasTagMetaData(node):
        return eval(cmds.getAttr('{}.{}'.format(node, tags.TAGS_META_DATA_ATTR)))
    else:
        log.warning('%s does NOT have the %s attribute.', node, tags.TAGS_META_DATA_ATTR)
        return None


def popTagFromMetaData(node, tag):
    """Removes the tag from the meta data attribute on the node.

    :parameters:
        node : str
            The node to remove the tag meta data from.

        tag : str
            The tag to remove from the meta data attribute
    """
    if hasTagMetaData(node):
        metaData = getTagMetaData(node)
        if tag in metaData:
            metaData.pop(tag)
        setTagMetaData(node, metaData)


def setTagMetaData(node, metaData):
    """Sets the meta data to the data given.

    :parameters:
        node : str
            The node to set the meta data on.

        metaData : dict
            The data to set on the meta data attribute. Converts to string.
    """
    if hasTagMetaData(node):
        resetTagMetaData(node)
        cmds.setAttr('{}.{}'.format(node, tags.TAGS_META_DATA_ATTR), lock=False)
        cmds.setAttr('{}.{}'.format(node, tags.TAGS_META_DATA_ATTR), metaData, type='string')
        cmds.setAttr('{}.{}'.format(node, tags.TAGS_META_DATA_ATTR), lock=True)


def updateTagMetaData(node, tag, validDicts=tags.STANDARD_TAGS_LIST):
    """Updates the tag meta data attribute on the node for the given tag.

    :parameters:
        node : str
            The node containing the meta data attribute.

        tag : str
            The tag to update on the meta data attribute

        validDicts : list
            The list of dictionaries containing tags as keys. Will use \
            this to find the descriptions and associations
    """
    metaData = getTagMetaData(node)

    username = os.getlogin()
    timestamp = datetime.datetime.now().strftime('%d-%b-%Y (%H:%M:%S)')

    assoc = getTagAssociation(tag, validDicts=validDicts)
    desc = getTagDescription(tag, validDicts=validDicts)

    metaData[tag] = {'User' : username,
                     'Timestamp' : timestamp,
                     'Association' : assoc,
                     'Description' : desc}

    cmds.setAttr('{}.{}'.format(node, tags.TAGS_META_DATA_ATTR), lock=False)
    cmds.setAttr('{}.{}'.format(node, tags.TAGS_META_DATA_ATTR), metaData, type='string')
    cmds.setAttr('{}.{}'.format(node, tags.TAGS_META_DATA_ATTR), lock=True)


def updateAllTagMetaData(node, validDicts=tags.STANDARD_TAGS_LIST):
    """Updates tag meta data attribute on the node for all tags.

    :parameters:
        node : str
            The node containing the meta data attribute.

        validDicts : str
            The pre defined dictionaries with tags as keys
    """
    if hasTagMetaData(node):
        for dictionary in validDicts:
            for tag in dictionary:
                if cmds.attributeQuery(tag, n=node, exists=True):
                    updateTagMetaData(node, tag, validDicts=validDicts)


def isTagValid(tag, validDicts=tags.STANDARD_TAGS_LIST):
    """Checks if the tag is in a pre-defined dict.

    :parameters:
        tag : str
            The name of the tag.

        validDicts : list of dict
            A list of dicts to check if the tag exists within.

    :return: The state of whether the tag is pre-defined.
    :rtype: bool
    """
    valid = False
    for dictionary in validDicts:
        if tag in dictionary:
            valid = True
    if not valid:
        log.debug('tag %s is not a valid tag', tag)
    return valid


def getValidDictsWithTag(tag, validDicts=tags.STANDARD_TAGS_LIST):
    """Gets the valid dict(s) that contain the given tag. \
    The tag must be the key in the dictionary.

    :parameters:
        tag : str
            The name of the tag.

        validDicts : list of dict
            A list of dicts to check if the tag exists within.

    :return: The list of dictionaries containing the tag.
    :rtype: list
    """
    l = []
    for dictionary in validDicts:
        if tag in dictionary:
            l.append(dictionary)
    if not l:
        log.warning('tag %s is NOT in any valid dictionaries', tag)
    return l


def getTagDescription(tag, validDicts=tags.STANDARD_TAGS_LIST, forceChoice=None):
    """Gets the description(s) of a tag from the list of valid dicts. \
    The tag must be the key in the dictionary.

    :parameters:
        tag : str
            The name of the tag.

        validDicts : list of dict
            A list of dicts to check for with the tag.

        forceChoice : None or int
            This is to be used to specify a choice if you know there are \
            multiple descriptions. Useful for hard coding purposes. :)

    :return: The description for the term within the validDicts
    :rtype: list
    """
    desc = []
    if isTagValid(tag, validDicts=validDicts):
        for dictionary in validDicts:
            if tag in dictionary and dictionary not in desc:
                desc.append(dictionary[tag]['Description'])
    if len(desc) < 1:
        log.debug('no descriptions found for tag %s', tag)
        return 'N/A'
    elif len(desc) == 1:
        return desc[0]
    elif len(desc) > 1:
        log.warning('multiple descriptions found for tag %s. requesting input... '
                    'will open a dialog but if you want, you can force a selection with '
                    'with the forceChoice flag', tag)
        if forceChoice is not None:
            try:
                return desc[forceChoice]
            except:
                raise
        else:
            choice = dialog.getQuickChoice(desc, message='Select a description for tag {}.'.format(tag))
            return choice


def getTagAssociation(tag, validDicts=tags.STANDARD_TAGS_LIST, forceChoice=None):
    """Gets the association(s) of a tag from the list of valid dicts. \
    The tag must be the key in the dictionary.

    :parameters:
        tag : str
            The name of the tag.

        validDicts : list of dict
            A list of dicts to check for with the tag.

        forceChoice : None or int
            This is to be used to specify a choice if you know there are \
            multiple associations. Useful for hard coding purposes. :)

    :return: The association for the term within the validDicts
    :rtype: str
    """
    assoc = []
    if isTagValid(tag, validDicts=validDicts):
        for dictionary in validDicts:
            if tag in dictionary and dictionary not in assoc:
                assoc.append(dictionary[tag]['Association'])
    if len(assoc) < 1:
        log.debug('no associations found for tag %s', tag)
        return 'N/A'
    elif len(assoc) == 1:
        return assoc[0]
    elif len(assoc) > 1:
        log.warning('multiple descriptions found for tag %s. requesting input... '
                    'will open a dialog but if you want, you can force a selection with '
                    'with the forceChoice flag', tag)
        if forceChoice is not None:
            try:
                return assoc[forceChoice]
            except:
                raise
        else:
            choice = dialog.getQuickChoice(assoc, message='Select an association for tag {}.'.format(tag))
            return choice


# ----------------------------------------------------------------------------#
# ----------------------------------------------------------------- Classes --#


class Tag(object):
    def __init__(self,
                 name='',
                 association='',
                 description='',
                 dataType='',
                 default=None):
        self.name = name
        self.association = association
        self.description = description
        self.dataType = dataType
        self.default = default
        self.value = default

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name:
            self._name = name
        else:
            raise ValueError("Cant set name property to empty string.")

    @property
    def association(self):
        return self._association

    @association.setter
    def association(self, association):
        if association:
            self._association = association
        else:
            raise ValueError("Cant set association property to empty string.")

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        if description:
            self._description = description
        else:
            raise ValueError("Cant set description property to empty string.")

    @property
    def dataType(self):
        return self._dataType

    @dataType.setter
    def dataType(self, dataType):
        if dataType is 'string':
            self._dataType = str
        elif dataType is 'int':
            self._dataType = int
        elif dataType is 'float':
            self._dataType = float
        elif dataType is 'bool':
            self._dataType = bool
        elif dataType is 'dict':
            self._dataType = dict

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, default):
        if self._isValueValid(default):
            self._default = default
        else:
            raise ValueError("Data type is incorrect. Try using data type: {}".format(self.dataType))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def _isValueValid(self, value):
        if type(value) is self._dataType:
            return True
        else:
            return False



