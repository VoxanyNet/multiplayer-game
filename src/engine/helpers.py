from typing

def get_matching_objects(collection, object_type):
    entities = []

    if collection.__class__ == dict: 
        for value in collection.values():
            if isinstance(value, object_type): 
                entities.append(value)

            elif value.__class__ == dict or list:
                new_entities = get_matching_objects(value, object_type)

                entities += new_entities

    elif collection.__class__ == list:
        for value in collection:
            if isinstance(value, object_type):
                entities.append(value)

            elif value.__class__ == dict or list:

                new_entities = get_matching_objects(value, object_type) 

                entities += new_entities
    
    return entities

def dict_diff(dict1: dict, dict2: dict):
    diff_dict = {}
    for key in dict2.keys():
        if key in dict1.keys() and dict1[key] != dict2[key]:
            diff_dict[key] = dict2[key]
    return diff_dict