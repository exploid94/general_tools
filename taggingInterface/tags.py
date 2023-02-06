RIG_TAGS = {
    'rigHookup': {
        'Association': 'MR3',
        'Description': 'Marks geometry that will be attached in the body rig.'
    },
    'reparentDuringUpdate': {
        'Association': 'MR3',
        'Description': 'Marks transforms that need its children re-parented to hierarchy during an update.'
    },
    'unparentDuringUpdate': {
        'Association': 'MR3',
        'Description': 'Marks transform to be removed from the Control_Rig transform hierarchy.'
    },
    'ignoreDuringUpdate': {
        'Association': 'MR3',
        'Description': 'Ignores being flagged as foreign transforms.'
    },
    'owningModuleID': {
        'Association': 'MR3',
        'Description': 'Marks a transform belonging to a module.'
    },
    'removeAtPublish': {
        'Association': 'Staging',
        'Description': 'Marks a node for removal during staging.'
    },
    'replaceAtPublish': {
        'Association': 'Staging',
        'Description': 'Marks a node for replacement during staging.'
    },
    'optimizeDeformerStack': {
        'Association': 'Deformer Interface',
        'Description': 'Marks deformed geo that should be optimized during staging'
    }
}

ANIM_TAGS = {}
CFX_TAGS = {}
FX_TAGS = {}
MODEL_TAGS = {}
CROWD_TAGS = {}
COMP_TAGS = {}

DUMMY_TAGS = {
    'stringSomething': {
        'Association': 'Dummy',
        'Description': 'This is a string attr.',
        'Type': str,
        'Default': 'something',
        'Value': 'something else'
    },
    'boolSomething': {
        'Association': 'Dummy',
        'Description': 'This is a bool attr.',
        'Type': bool,
        'Default': 0,
        'Value': 1
    },
    'floatSomething': {
        'Association': 'Dummy',
        'Description': 'This is a float attr.',
        'Type': float,
        'Default': 0.0,
        'Value': 1.0
    },
    'intSomething': {
        'Association': 'Dummy',
        'Description': 'This is an int attr.',
        'Type': int,
        'Default': 1,
        'Value': 2
    },
    'listSomething': {
        'Association': 'Dummy',
        'Description': 'This is a list attr.',
        'Type': list,
        'Default': [],
        'Value': ['something']
    },
    'tupleSomething': {
        'Association': 'Dummy',
        'Description': 'This is a tuple attr.',
        'Type': tuple,
        'Default': (),
        'Value': (0, 1, 2)
    },
    'dictSomething': {
        'Association': 'Dummy',
        'Description': 'This is a dict attr.',
        'Type': dict,
        'Default': {},
        'Value': {'key': 'value'}
    },

}

STANDARD_TAGS_LIST = [
    RIG_TAGS,
    ANIM_TAGS,
    CFX_TAGS,
    FX_TAGS,
    MODEL_TAGS,
    CROWD_TAGS,
    COMP_TAGS,
]

DEPARTMENT_TAGS = {
    'rig':RIG_TAGS,
    'anim':ANIM_TAGS,
    'cfx':CFX_TAGS,
    'fx':FX_TAGS,
    'model':MODEL_TAGS,
    'crowd':CROWD_TAGS,
    'comp': COMP_TAGS
}

COMMON_TERMS = [
    "ignore",
    "parent",
    "reparent",
    "unparent",
    "child",
    "children",
    "before",
    "during",
    "after",
    "publish",
    "stage",
    "control",
    "wip",
    "module",
    "update"
]

TAGS_META_DATA_ATTR = 'tagsMetaData'
