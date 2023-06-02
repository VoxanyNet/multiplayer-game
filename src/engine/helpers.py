from typing import Union, List, Type

def get_matching_objects(collection: Union[dict, list], object_type):
    """Recursively search through a dictionary or list to find objects of given type"""
    matching_objects: List[Type[object_type]] = []

    if collection.__class__ == dict: 
        for value in collection.values():
            if isinstance(value, object_type): 
                matching_objects.append(value)

            elif value.__class__ == dict or list:
                matching_objects += get_matching_objects(value, object_type)

    elif collection.__class__ == list:
        for value in collection:
            if isinstance(value, object_type):
                matching_objects.append(value)

            elif value.__class__ == dict or list:

                matching_objects += get_matching_objects(value, object_type) 
    
    return matching_objects

def dict_diff(dict1: dict, dict2: dict):
    diff_dict = {}
    for key in dict2.keys():
        if key in dict1.keys() and dict1[key] != dict2[key]:
            diff_dict[key] = dict2[key]
    return diff_dict