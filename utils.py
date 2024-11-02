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
        "instructions": [] if pd.isna(exercise_info["instructions"]) else str(exercise_info["instructions"]).split('\n'),
        "fields": [],
        "link": "",
        "modality": "66013e83b117d35345209b07",
        "preview_300": "",
        "share": 0,
        "picture": [],
        "thumbnail_url": "",
        "video": "",
        "videoLink": "" if pd.isna(exercise_info.get("video_link", "")) else exercise_info.get("video_link", ""),
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
            "exercise_name": exercise_df.at[i, "EXERCISE NAME"],
            "video_status": exercise_df.at[i, "VIDEO STATUS"],
            "description":  exercise_df.at[i, "Description"],
            "modality":  exercise_df.at[i, "Modality"],
            "muscle_groups": [
                exercise_df.at[i, "Muscle group"],
                exercise_df.at[i, "Muscle group 2"],
                exercise_df.at[i, "Muscle group 3"]
            ],
            "movement_patterns":  [
                exercise_df.at[i, "Movement pattern 1"],
                exercise_df.at[i, "Movement pattern 2"],
                exercise_df.at[i, "Movement pattern 3"]
            ],
            "category":  exercise_df.at[i, "Category"],
            "tracking_fields":  exercise_df.at[i, "Tracking fields"],
            "instructions": exercise_df.at[i, "Instructions"],
            "video_link": exercise_df.at[i, "Video link"],
            "tags": {
                "exercise_level_1": exercise_df.at[i, "Basic"],
                "exercise_level_2": exercise_df.at[i, "Intermediate"],
                "exercise_level_3": exercise_df.at[i, "Advanced"],
                "skill_name_1": exercise_df.at[i, "SKILL NAME 1"],
                "skill_name_2": exercise_df.at[i, "SKILL NAME 2"],
                "skill_name_3": exercise_df.at[i, "SKILL NAME 3"],
                "calisthenics": exercise_df.at[i, "Calisthenics"],
                "wx_athlete": exercise_df.at[i, "WX Athlete"],
                "hp_gymnast": exercise_df.at[i, "HP gymnast"],
                "equipment_1": exercise_df.at[i, "EQUIPMENT 1"],
                "equipment_2": exercise_df.at[i, "EQUIPMENT 2"],
                "equipment_3": exercise_df.at[i, "EQUIPMENT 3"],
                "equipment_4": exercise_df.at[i, "EQUIPMENT 4"],
                "warm_up": exercise_df.at[i, "Warm up"],
                "cardio": exercise_df.at[i, "Cardio"],
                "crossfit_lift": exercise_df.at[i, "Crossfit lift"],
                "bodyweight": exercise_df.at[i, "Bodyweight"],
                "weight": exercise_df.at[i, "Weight"],
                "band_resistance": exercise_df.at[i, "Band resistance"],
                "weightlifting": exercise_df.at[i, "Weightlifting"],
                "mobility": exercise_df.at[i, "mobility"],
                "active": exercise_df.at[i, "active"],
                "passive": exercise_df.at[i, "passive"],
                "stretching": exercise_df.at[i, "stretching"],
                "upperbody": exercise_df.at[i, "Upperbody"],
                "lowerbody": exercise_df.at[i, "Lowerbody"],
                "core": exercise_df.at[i, "Core"],
                "push": exercise_df.at[i, "Push"],
                "pull": exercise_df.at[i, "Pull"],
                "arms_straight": exercise_df.at[i, "Arms straight"],
                "arms_bend": exercise_df.at[i, "Arms bend"],
                "iso": exercise_df.at[i, "Iso"],
                "plyo": exercise_df.at[i, "Plyo"],
                "set": exercise_df.at[i, "Set"],
                "shoulders": exercise_df.at[i, "Shoulders"],
                "pecs": exercise_df.at[i, "Pecs"],
                "triceps": exercise_df.at[i, "Triceps"],
                "biceps": exercise_df.at[i, "Biceps"],
                "back": exercise_df.at[i, "Back"],
                "abs": exercise_df.at[i, "Abs"],
                "lower_back": exercise_df.at[i, "Lower back"],
                "obliques": exercise_df.at[i, "Obliques"],
                "glute": exercise_df.at[i, "Glute"],
                "quads": exercise_df.at[i, "Quads"],
                "hamstrings": exercise_df.at[i, "Hamstrings"],
                "calves": exercise_df.at[i, "Calves"],
                "wrist": exercise_df.at[i, "Wrist"],
                "hips": exercise_df.at[i, "Hips"],
                "elbows": exercise_df.at[i, "Elbows"],
                "ankle": exercise_df.at[i, "Ankle"],
                "thoracic": exercise_df.at[i, "Thoracic"],
                "forearms": exercise_df.at[i, "Forearms"],
                "neck": exercise_df.at[i, "Neck"],
                "pull_up": exercise_df.at[i, "Pull up"],
                "push_up": exercise_df.at[i, "Push up"],
                "dip": exercise_df.at[i, "Dip"],
                "row": exercise_df.at[i, "Row"],
                "press": exercise_df.at[i, "Press"],
                "curl": exercise_df.at[i, "Curl"],
                "squat": exercise_df.at[i, "Squat"],
                "bridge": exercise_df.at[i, "Bridge"],
                "throws": exercise_df.at[i, "Throws"],
                "slams": exercise_df.at[i, "Slams"],
                "sit_up": exercise_df.at[i, "Sit up"],
                "leg_lift": exercise_df.at[i, "Leg lift"],
                "balance": exercise_df.at[i, "Balance"],
                "raise": exercise_df.at[i, "Raise"],
                "rocks": exercise_df.at[i, "Rocks"],
                "arch-hollow_shape": exercise_df.at[i, "Arch-hollow shape"],
                "rotation": exercise_df.at[i, "Rotation"],
                "gymnastics_skill": exercise_df.at[i, "Gymnastics skill"],
                "plank": exercise_df.at[i, "Plank"],
                "preS_explosive": exercise_df.at[i, "PreS explosive"],
                "preS_legs": exercise_df.at[i, "PreS legs"],
                "postS_legs": exercise_df.at[i, "PostS legs"],
                "postS_rings": exercise_df.at[i, "PostS rings"],
                "postS_altern_rings": exercise_df.at[i, "PostS altern rings"],
                "postS_weights": exercise_df.at[i, "PostS weights"],
            }  
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