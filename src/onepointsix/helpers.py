from typing import Union, List, Type
import sys

def get_matching_objects(collection: Union[dict, list], object_type):
    """Recursively search through a dictionary or list to find objects of given type"""
    matching_objects: List[Type[object_type]] = []

    if type(collection) == dict: 
        for value in collection.values():
            if isinstance(value, object_type): 
                matching_objects.append(value)

            elif type(value) == dict or type(value) == list:
                matching_objects += get_matching_objects(value, object_type)

    elif type(collection) == list:
        for value in collection:
            if isinstance(value, object_type):
                matching_objects.append(value)

            elif type(value) == dict or type(value) == list:

                matching_objects += get_matching_objects(value, object_type) 
    
    return matching_objects

def dict_diff(dict1: dict, dict2: dict):
    diff_dict = {}

    for key, value in dict2.items():

        if key not in dict1.keys():
            diff_dict[key] = value
            
            print("omg!!! it happened!!! there was a new attribute and you saved yourself anguish!!!")
            sys.exit()
        
        # recursively check for diffs in sub dictionaries
        elif type(value) is dict:
        
            sub_diff_dict = dict_diff(dict1[key], value)

            if sub_diff_dict == {}:
                # we dont needa include this sub dict attribute if there were no diffs in its value!!!!
                continue

            diff_dict[key] = sub_diff_dict

        # keys that exist in both but just changed
        elif key in dict1.keys() and dict1[key] != dict2[key]:
            diff_dict[key] = value
            
    return diff_dict