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

# Third party
from maya import cmds

# Custom
from rig_tools.tool.correctIt import correctItUI

# ----------------------------------------------------------------------------#
# ----------------------------------------------------------------- GLOBALS --#
log = logging.getLogger(__name__)


# ----------------------------------------------------------------------------#
# --------------------------------------------------------------- FUNCTIONS --#


# ----------------------------------------------------------------------------#
# ----------------------------------------------------------------- Classes --#