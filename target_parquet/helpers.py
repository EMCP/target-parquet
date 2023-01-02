try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping  # deprecated in Python 3.3

import singer
import os

LOGGER = singer.get_logger()
LOGGER.setLevel(os.getenv("LOGGER_LEVEL", "INFO"))


def flatten(dictionary, parent_key="", sep="__"):
    """Function that flattens a nested structure, using the separator given as parameter, or uses '__' as default
    E.g:
     dictionary =  {
                        'key_1': 1,
                        'key_2': {
                               'key_3': 2,
                               'key_4': {
                                      'key_5': 3,
                                      'key_6' : ['10', '11']
                                 }
                        }
                       }
    By calling the function with the dictionary above as parameter, you will get the following strucure:
        {
             'key_1': 1,
             'key_2__key_3': 2,
             'key_2__key_4__key_5': 3,
             'key_2__key_4__key_6': "['10', '11']"
         }
    """
    items = []
    for k, v in dictionary.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v) if type(v) is list else v))
    return dict(items)


def flatten_schema(dictionary, parent_key="", sep="__"):
    """Function that flattens a nested structure, using the separator given as parameter, or uses '__' as default
    E.g:
     dictionary =  {
                        'key_1': {'type': ['null', 'integer']},
                        'key_2': {
                            'type': ['null', 'object'],
                            'properties': {
                                'key_3': {'type': ['null', 'string']},
                                'key_4': {
                                    'type': ['null', 'object'],
                                    'properties': {
                                        'key_5' : {'type': ['null', 'integer']},
                                        'key_6' : {
                                            'type': ['null', 'array'],
                                            'items': {
                                                'type': ['null', 'object'],
                                                'properties': {
                                                    'key_7': {'type': ['null', 'number']},
                                                    'key_8': {'type': ['null', 'string']}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
    By calling the function with the dictionary above as parameter, you will get the following strucure:
        [
             'key_1',
             'key_2__key_3',
             'key_2__key_4__key_5',
             'key_2__key_4__key_6'
        ]
    """
    items = []
    if dictionary:
        for k, v in dictionary.items():
            new_key = parent_key + sep + k if parent_key else k
            if "type" not in v:
                LOGGER.warning(f"SCHEMA with limited support on field {k}: {v}")
            if "object" in v.get("type", []):
                items.extend(flatten_schema(v.get("properties"), new_key, sep=sep))
            else:
                items.append(new_key)
    return items
