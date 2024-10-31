from config import *
from api import *

import pandas as pd

def get_payload(session, access_token, exercise_info, exercise_df):
    """
    Constructs the payload for uploading an exercise to the Everfit API.

    Args:
        session (requests.Session): The active session used for making requests.
        access_token (str): The access token for authenticating API requests.
        exercise_info (dict): A dictionary containing detailed information about the exercise.

    Returns:
        dict: A dictionary representing the payload with exercise details, ready to be sent to the API.
    """
   
    # Default payload
    payload = {
        "author": "666c67f6c98eb80026f047c9",
        "author_name": "Ruben Lopez Martinez", 
        "title": exercise_info["exercise_name"],
        "instructions": [] if pd.isna(exercise_info.get("instructions", [])) else exercise_info.get("instructions", []),
        "fields": [],
        "link": "",
        "modality": "66013e83b117d35345209b07",
        "preview_300": "",
        "share": 0,
        "picture": [],
        "thumbnail_url": "",
        "video": "",
        "videoLink": "",
    }
    
    # Category Type (required)
    category = exercise_info.get("category", "strength")
    payload["category_type"] = CATEGORY_TYPE_MAP.get(str(category).lower().replace(" ", ""), "5cd912c319ae01d22ea76012") # else its the strength category id
    payload["category_type_name"] = "strength" if pd.isna(category) else category

    # Modality (optional, but has default)
    modality = exercise_info["modality"]
    if not pd.isna(modality):
        payload["modality"] = MODALITY_MAP.get(str(modality).lower().replace(" ", ""), "")

    # Movement Patterns (optional)
    movement_patterns = []
    for idx, pattern in enumerate(exercise_info["movement_patterns"]):
        if not pd.isna(pattern):
            movement_patterns.append({
                "is_primary": idx == 0,
                "movement_pattern": MOVEMENT_PATTERN_MAP.get(str(pattern).lower().replace(" ", ""), "")
            })
    if movement_patterns:
        payload["movement_patterns"] = movement_patterns

    # Muscle Groups (optional)
    muscle_groups = []
    for idx, muscle in enumerate(exercise_info["muscle_groups"]):
        if not pd.isna(muscle):
            muscle_groups.append({
                "is_primary": idx == 0,
                "muscle_group": MUSCLE_GROUP_MAP.get(str(muscle).lower().replace(" ", ""), "")
            })
    if muscle_groups:
        payload["muscle_groups"] = muscle_groups

    # Tracking Fields (optional)
    tracking_fields = exercise_info["tracking_fields"].split(',') if not pd.isna(exercise_info["tracking_fields"]) else []
    for i in range(len(tracking_fields)):
        payload["fields"].append(TRACKING_FIELDS_MAP.get(str(tracking_fields[i]).lower().replace(" ", ""), ""))
    payload["fields"].append("5cd912bb19ae01d22ea76011")  # they always add this "Rest" one at the end for some reason
    
    # Tags
    tags = []
    requested_tags = get_requested_tags(exercise_df, exercise_info)
    tag_list = get_tag_list(session, access_token)
    tag_mappings = create_tag_mappings(tag_list)

    # Add or create tag id
    for requested_tag in requested_tags:
        if requested_tag in tag_mappings:
            tag_id = tag_mappings[requested_tag]
            tags.append(tag_id)
        else:
            tag_id = create_new_tag_id(session, access_token, requested_tag)
            tags.append(tag_id)
    payload["tags"] = tags

    # Video link
    video_link = exercise_info.get("video_link", "")
    payload["videoLink"] = video_link

    return payload

def get_exercises_list(start_index, exercise_df):
    """
    Extracts a list of exercises and their associated information from a DataFrame.

    Args:
        start_index (int): The row index from which to start reading exercise data.
        exercise_df (DataFrame): The DataFrame containing exercise information.

    Returns:
        list: A list of dictionaries, each containing detailed information about an exercise.
    """

    # Creates a list of exercises with information
    exercises_list = []

    # Goes through each cell with an exercise, adding info to list of exercises
    for i in range(start_index, len(exercise_df)):
        # Breaks if at end
        if pd.isna(exercise_df.iloc[i, 0]):
            break
        
        # Moves to next if video status is a 2 (already uploaded into Everfit) or 0 (not ready)
        if exercise_df.iloc[i, 1] != 1:
            continue
        
        # Creates a dictionary of exercise info
        exercise_info = {
            "exercise_name": exercise_df.iloc[i, 0],
            "video_status": exercise_df.iloc[i, 1],
            "description":  exercise_df.iloc[i, 2],
            "modality":  exercise_df.iloc[i, 3],
            "muscle_groups": [
                exercise_df.iloc[i, 4],
                exercise_df.iloc[i, 5],
                exercise_df.iloc[i, 6]
            ],
            "movement_patterns":  [
                exercise_df.iloc[i, 7],
                exercise_df.iloc[i, 8],
                exercise_df.iloc[i, 9]
            ],
            "category":  exercise_df.iloc[i, 10],
            "tracking_fields":  exercise_df.iloc[i, 11],
            "instructions": exercise_df.iloc[i, 12],
            "tags": {
                "exercise_level_1": exercise_df.iloc[i, 13],
                "exercise_level_2": exercise_df.iloc[i, 14],
                "exercise_level_3": exercise_df.iloc[i, 15],
                "skill_name_1": exercise_df.iloc[i, 16],
                "skill_name_2": exercise_df.iloc[i, 17],
                "skill_name_3": exercise_df.iloc[i, 18],
                "calisthenics": exercise_df.iloc[i, 19],
                "wx_athlete": exercise_df.iloc[i, 20],
                "hp_gymnast": exercise_df.iloc[i, 21],
                "equipment_1": exercise_df.iloc[i, 22],
                "equipment_2": exercise_df.iloc[i, 23],
                "equipment_3": exercise_df.iloc[i, 24],
                "equipment_4": exercise_df.iloc[i, 25],
                "warm_up": exercise_df.iloc[i, 26],
                "cardio": exercise_df.iloc[i, 27],
                "crossfit_lift": exercise_df.iloc[i, 28],
                "bodyweight": exercise_df.iloc[i, 29],
                "weight": exercise_df.iloc[i, 30],
                "band_resistance": exercise_df.iloc[i, 31],
                "weightlifting": exercise_df.iloc[i, 32],
                "mobility": exercise_df.iloc[i, 33],
                "active": exercise_df.iloc[i, 34],
                "passive": exercise_df.iloc[i, 35],
                "stretching": exercise_df.iloc[i, 36],
                "upperbody": exercise_df.iloc[i, 37],
                "lowerbody": exercise_df.iloc[i, 38],
                "core": exercise_df.iloc[i, 39],
                "push": exercise_df.iloc[i, 40],
                "pull": exercise_df.iloc[i, 41],
                "arms_straight": exercise_df.iloc[i, 42],
                "arms_bend": exercise_df.iloc[i, 43],
                "iso": exercise_df.iloc[i, 44],
                "plyo": exercise_df.iloc[i, 45],
                "set": exercise_df.iloc[i, 46],
                "shoulders": exercise_df.iloc[i, 47],
                "pecs": exercise_df.iloc[i, 48],
                "triceps": exercise_df.iloc[i, 49],
                "biceps": exercise_df.iloc[i, 50],
                "back": exercise_df.iloc[i, 51],
                "abs": exercise_df.iloc[i, 52],
                "lower_back": exercise_df.iloc[i, 53],
                "obliques": exercise_df.iloc[i, 54],
                "glute": exercise_df.iloc[i, 55],
                "quads": exercise_df.iloc[i, 56],
                "hamstrings": exercise_df.iloc[i, 57],
                "calves": exercise_df.iloc[i, 58],
                "wrist": exercise_df.iloc[i, 59],
                "hips": exercise_df.iloc[i, 60],
                "elbows": exercise_df.iloc[i, 61],
                "ankle": exercise_df.iloc[i, 62],
                "thoracic": exercise_df.iloc[i, 63],
                "forearms": exercise_df.iloc[i, 64],
                "neck": exercise_df.iloc[i, 65],
                "pull_up": exercise_df.iloc[i, 66],
                "push_up": exercise_df.iloc[i, 67],
                "dip": exercise_df.iloc[i, 68],
                "row": exercise_df.iloc[i, 69],
                "press": exercise_df.iloc[i, 70],
                "curl": exercise_df.iloc[i, 71],
                "squat": exercise_df.iloc[i, 72],
                "bridge": exercise_df.iloc[i, 73],
                "throws": exercise_df.iloc[i, 74],
                "slams": exercise_df.iloc[i, 75],
                "sit_up": exercise_df.iloc[i, 76],
                "leg_lift": exercise_df.iloc[i, 77],
                "balance": exercise_df.iloc[i, 78],
                "raise": exercise_df.iloc[i, 79],
                "rocks": exercise_df.iloc[i, 80],
                "arch-hollow_shape": exercise_df.iloc[i, 81],
                "rotation": exercise_df.iloc[i, 82],
                "gymnastics_skill": exercise_df.iloc[i, 83],
                "plank": exercise_df.iloc[i, 84],
                "preS_explosive": exercise_df.iloc[i, 85],
                "preS_legs": exercise_df.iloc[i, 86],
                "postS_legs": exercise_df.iloc[i, 87],
                "postS_rings": exercise_df.iloc[i, 88],
                "postS_altern_rings": exercise_df.iloc[i, 89],
                "postS_weights": exercise_df.iloc[i, 90],
            },
            "video_link": exercise_df.iloc[i, 91] if not pd.isna(exercise_df.iloc[i, 91]) else ""
        }

        # Adds to list of exercises
        exercises_list.append(exercise_info)

    return exercises_list

def create_tag_mappings(tag_list):
    """
    Creates a dictionary mapping tag names to their corresponding IDs.

    Args:
        tag_list (list): A list of dictionaries where each dictionary contains
                         'name' and '_id' fields representing a tag.

    Returns:
        dict: A dictionary where keys are tag names and values are tag IDs.
    """
    tag_mappings = {}
    for tag in tag_list:
        tag_mappings[tag['name']] = tag['_id']
    return tag_mappings

def get_requested_tags(exercise_df, exercise_info):
    """
    Retrieves a list of requested tags based on exercise information.

    Args:
        exercise_df (DataFrame): The DataFrame containing the exercise data.
        exercise_info (dict): A dictionary containing details about the exercise, 
                              including a 'tags' field.

    Returns:
        list: A list of tag names associated with the exercise.
    """
    requested_tags = []
    cur_tag_col = 12
    # Goes through each tag, adding the proper tag name to the list
    for key, val in exercise_info['tags'].items():
        cur_tag_col += 1
        # Skip if na or 0
        if pd.isna(val) or val == 0:
            continue
        # Add row name if integer, else add the value
        if isinstance(val, int):
            col_name = exercise_df.iloc[1, cur_tag_col]
            requested_tags.append(col_name)
        else:
            requested_tags.append(val)
    return requested_tags