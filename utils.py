from config import *
from api import *

import pandas as pd

# Helper function to safely get string values
def safe_str(value, default=""):
    if pd.isna(value) or value is None:
        return default
    return str(value)

# Helper function to safely get DataFrame values
def safe_get(df, index, column, default=None):
    if column in df.columns:
        value = df.at[index, column]
        return value if not pd.isna(value) else default
    return default

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
        "title": safe_str(exercise_info.get("exercise_name")),
        "instructions": [] if pd.isna(exercise_info["instructions"]) else safe_str(exercise_info["instructions"]).split('\n'),
        "fields": [],
        "link": "",
        "modality": "66013e83b117d35345209b07",
        "preview_300": "",
        "share": 0,
        "picture": [],
        "thumbnail_url": "",
        "video": "",
        "videoLink": "" if pd.isna(exercise_info.get("video_link", "")) else safe_str(exercise_info.get("video_link", "")),
    }
    
    # Category Type (required)
    category = exercise_info.get("category", "strength")
    if pd.isna(category) or category is None:
        category = "strength"
    category_key = safe_str(category).lower().replace(" ", "")
    payload["category_type"] = CATEGORY_TYPE_MAP.get(category_key, "5cd912c319ae01d22ea76012") # else its the strength category id
    payload["category_type_name"] = category

    # Modality (optional, but has default)
    modality = exercise_info.get("modality")
    if not pd.isna(modality) and modality is not None:
        modality_key = safe_str(modality).lower().replace(" ", "")
        payload["modality"] = MODALITY_MAP.get(modality_key, "")
        # error
        if payload["modality"] == "":
            raise Exception(f"Modality {modality} not recognized.")

    # Movement Patterns (optional)
    movement_patterns = []
    for idx, pattern in enumerate(exercise_info.get("movement_patterns", [])):

        if pd.isna(pattern) or pattern is None or pattern == "":
            continue

        pattern_key = safe_str(pattern).lower().replace(" ", "")
        movement_pattern_id = MOVEMENT_PATTERN_MAP.get(pattern_key, "")
        if movement_pattern_id == "":
            raise Exception(f"Movement pattern '{pattern}' not recognized.")
        elif any(d['movement_pattern'] == movement_pattern_id for d in movement_patterns):
            continue
        movement_patterns.append({
            "is_primary": idx == 0,
            "movement_pattern": movement_pattern_id
        })
    if movement_patterns:
        payload["movement_patterns"] = movement_patterns

    # Muscle Groups (optional)
    muscle_groups = []
    for idx, muscle in enumerate(exercise_info.get("muscle_groups", [])):
        if pd.isna(muscle) or muscle is None or muscle == "":
            continue
        muscle_key = safe_str(muscle).lower().replace(" ", "")
        muscle_group_id = MUSCLE_GROUP_MAP.get(muscle_key, "")
        if muscle_group_id == "":
            raise Exception(f"Muscle group '{muscle}' not recognized.")
        elif any(d['muscle_group'] == muscle_group_id for d in muscle_groups):
            continue
        muscle_groups.append({
            "is_primary": idx == 0,
            "muscle_group": muscle_group_id
        })
    if muscle_groups:
        payload["muscle_groups"] = muscle_groups

    # Tracking Fields (optional)
    tracking_fields_str = exercise_info.get("tracking_fields", "")
    tracking_fields = []
    if not pd.isna(tracking_fields_str) and tracking_fields_str is not None:
        tracking_fields = [field.strip() for field in safe_str(tracking_fields_str).split(',') if field.strip()]
    for field in tracking_fields:
        field_key = field.lower().replace(" ", "")
        field_id = TRACKING_FIELDS_MAP.get(field_key, "")
        if field_id:
            payload["fields"].append(field_id)
    # Always add the "Rest" field
    payload["fields"].append("5cd912bb19ae01d22ea76011")
    
    # Tags
    tags = []
    requested_tags = get_requested_tags(exercise_df, exercise_info)
    tag_list = get_tag_list(session, access_token) or []
    tag_mappings = create_tag_mappings(tag_list)

    # Add or create tag id
    seen_tags = []
    for requested_tag in requested_tags:
        requested_tag = str(requested_tag)
        if requested_tag == "" or requested_tag is None or requested_tag in seen_tags:
            continue
        if requested_tag in tag_mappings:
            tag_id = tag_mappings[requested_tag]
        else:
            tag_id = create_new_tag_id(session, access_token, requested_tag)
        tags.append(tag_id)
        seen_tags.append(requested_tag)
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
        
        # Continue if video status is not 1
        video_status = safe_get(exercise_df, i, "VIDEO STATUS", 0)
        if video_status != 1:
            continue
        
        # Creates a dictionary of exercise info
        exercise_info = {
            "exercise_name": safe_get(exercise_df, i, "EXERCISE NAME", ""),
            "video_status": video_status,
            "description": safe_get(exercise_df, i, "EXERCISE NAME", ""),
            "modality": safe_get(exercise_df, i, "Modality", ""),
            "muscle_groups": [
                safe_get(exercise_df, i, "Muscle group", ""),
                safe_get(exercise_df, i, "Muscle group 2", ""),
                safe_get(exercise_df, i, "Muscle group 3", "")
            ],
            "movement_patterns":  [
                safe_get(exercise_df, i, "Movement pattern 1", ""),
                safe_get(exercise_df, i, "Movement pattern 2", ""),
                safe_get(exercise_df, i, "Movement pattern 3", "")
            ],
            "category": safe_get(exercise_df, i, "Category", "strength"),
            "tracking_fields": safe_get(exercise_df, i, "Tracking fields", ""),
            "instructions": safe_get(exercise_df, i, "Instructions", ""),
            "video_link": safe_get(exercise_df, i, "Video link", ""),
            "tags": {
                "exercise_level_1": safe_get(exercise_df, i, "Basic", 0),
                "exercise_level_2": safe_get(exercise_df, i, "Intermediate", 0),
                "exercise_level_3": safe_get(exercise_df, i, "Advanced", 0),
                "skill_name_1": safe_get(exercise_df, i, "SKILL NAME 1", ""), 
                "skill_name_2": safe_get(exercise_df, i, "SKILL NAME 2", ""), 
                "skill_name_3": safe_get(exercise_df, i, "SKILL NAME 3", ""), 
                "calisthenics": safe_get(exercise_df, i, "Calisthenics", 0),
                "wx_athlete": safe_get(exercise_df, i, "WX Athlete", 0),
                "hp_gymnast": safe_get(exercise_df, i, "HP gymnast", 0),
                "equipment_1": safe_get(exercise_df, i, "EQUIPMENT 1", ""), 
                "equipment_2": safe_get(exercise_df, i, "EQUIPMENT 2", ""), 
                "equipment_3": safe_get(exercise_df, i, "EQUIPMENT 3", ""), 
                "equipment_4": safe_get(exercise_df, i, "EQUIPMENT 4", ""), 
                "warm_up": safe_get(exercise_df, i, "Warm up", 0),
                "cardio": safe_get(exercise_df, i, "Cardio", 0),
                "crossfit_lift": safe_get(exercise_df, i, "Crossfit lift", 0),
                "bodyweight": safe_get(exercise_df, i, "Bodyweight", 0),
                "weight": safe_get(exercise_df, i, "Weight", 0),
                "band_resistance": safe_get(exercise_df, i, "Band resistance", 0),
                "weightlifting": safe_get(exercise_df, i, "Weightlifting", 0),
                "mobility": safe_get(exercise_df, i, "mobility", 0),
                "active": safe_get(exercise_df, i, "active", 0),
                "passive": safe_get(exercise_df, i, "passive", 0),
                "stretching": safe_get(exercise_df, i, "stretching", 0),
                "upperbody": safe_get(exercise_df, i, "Upperbody", 0),
                "lowerbody": safe_get(exercise_df, i, "Lowerbody", 0),
                "core": safe_get(exercise_df, i, "Core", 0),
                "push": safe_get(exercise_df, i, "Push", 0),
                "pull": safe_get(exercise_df, i, "Pull", 0),
                "arms_straight": safe_get(exercise_df, i, "Arms straight", 0),
                "arms_bend": safe_get(exercise_df, i, "Arms bend", 0),
                "iso": safe_get(exercise_df, i, "Iso", 0),
                "plyo": safe_get(exercise_df, i, "Plyo", 0),
                "set": safe_get(exercise_df, i, "Set", 0),
                "shoulders": safe_get(exercise_df, i, "Shoulders", 0),
                "pecs": safe_get(exercise_df, i, "Pecs", 0),
                "triceps": safe_get(exercise_df, i, "Triceps", 0),
                "biceps": safe_get(exercise_df, i, "Biceps", 0),
                "back": safe_get(exercise_df, i, "Back", 0),
                "abs": safe_get(exercise_df, i, "Abs", 0),
                "lower_back": safe_get(exercise_df, i, "Lower back", 0),
                "obliques": safe_get(exercise_df, i, "Obliques", 0),
                "glute": safe_get(exercise_df, i, "Glutes", 0),
                "quads": safe_get(exercise_df, i, "Quads", 0),
                "hamstrings": safe_get(exercise_df, i, "Hamstrings", 0),
                "calves": safe_get(exercise_df, i, "Calves", 0),
                "wrist": safe_get(exercise_df, i, "Wrist", 0),
                "hips": safe_get(exercise_df, i, "Hips", 0),
                "elbows": safe_get(exercise_df, i, "Elbows", 0),
                "ankle": safe_get(exercise_df, i, "Ankle", 0),
                "thoracic": safe_get(exercise_df, i, "Thoracic", 0),
                "forearms": safe_get(exercise_df, i, "Forearms", 0),
                "neck": safe_get(exercise_df, i, "Neck", 0),
                "pull_up": safe_get(exercise_df, i, "Pull up", 0),
                "push_up": safe_get(exercise_df, i, "Push up", 0),
                "dip": safe_get(exercise_df, i, "Dip", 0),
                "row": safe_get(exercise_df, i, "Row", 0),
                "press": safe_get(exercise_df, i, "Press", 0),
                "curl": safe_get(exercise_df, i, "Curl", 0),
                "squat": safe_get(exercise_df, i, "Squat", 0),
                "bridge": safe_get(exercise_df, i, "Bridge", 0),
                "throws": safe_get(exercise_df, i, "Throws", 0),
                "slams": safe_get(exercise_df, i, "Slams", 0),
                "sit_up": safe_get(exercise_df, i, "Sit up", 0),
                "leg_lift": safe_get(exercise_df, i, "Leg lift", 0),
                "balance": safe_get(exercise_df, i, "Balance", 0),
                "raise": safe_get(exercise_df, i, "Raise", 0),
                "rocks": safe_get(exercise_df, i, "Rocks", 0),
                "arch-hollow_shape": safe_get(exercise_df, i, "Arch-hollow shape", 0),
                "rotation": safe_get(exercise_df, i, "Rotation", 0),
                "gymnastics_skill": safe_get(exercise_df, i, "Gymnastics skill", 0),
                "plank": safe_get(exercise_df, i, "Plank", 0),
                "preS_explosive": safe_get(exercise_df, i, "PreS explosive", 0),
                "preS_legs": safe_get(exercise_df, i, "PreS legs", 0),
                "postS_legs": safe_get(exercise_df, i, "PostS legs", 0),
                "postS_rings": safe_get(exercise_df, i, "PostS rings", 0),
                "postS_altern_rings": safe_get(exercise_df, i, "PostS altern rings", 0),
                "postS_weights": safe_get(exercise_df, i, "PostS weights", 0),
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
    string_cols = ["SKILL NAME 1", "SKILL NAME 2", "SKILL NAME 3", "EQUIPMENT 1", "EQUIPMENT 2", "EQUIPMENT 3", "EQUIPMENT 4"]
    col_names = exercise_df.columns.tolist()
    cur_tag_col = col_names.index("Basic")

    # Goes through each tag, adding the proper tag name to the list
    for key, val in exercise_info.get('tags', {}).items():
        col_name = col_names[cur_tag_col]
        # Skip if na or 0
        if pd.isna(val) or val == 0 or val is None or val == "":
            cur_tag_col += 1
            continue
        # Add value if in string_cols, else add col name
        if col_name in string_cols:
            requested_tags.append(val)
        else:
            requested_tags.append(col_name)
        cur_tag_col += 1
            
    return requested_tags