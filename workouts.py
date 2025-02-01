from utils import *
from api import *
from config import *

import pandas as pd
import requests
import getpass
import collections
import json

# FUNCTIONALITY
# 1. Regular without supersets CHECK
# 2. Regular with supersets CHECK
# 3. Intervals 
# 4. EMOM - add reps, duration=60, rest=0
# 5. AMRAP
# 6. For time

# Status != 1, ignores CHECK

def min_to_seconds(minutes):
    return int(minutes*60)

def format_seconds_to_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02}:{seconds:02}"

def filter_section_type(section_type):
    string_parts = section_type.split(" ")
    if len(string_parts) > 1:
        string_parts = [string.lower() for string in string_parts]
        return "_".join(string_parts)
    else:
        return section_type.lower()

def get_individual_exercise_data(exercise_id, session, headers):
    # Used for getting each individual exercise details (base + exercise id)
    base_url = "https://api-prod3.everfit.io/api/exercise/detail/"

    try:
        # get id and request details
        detail_url = base_url + exercise_id
        response = session.get(detail_url, headers=headers, timeout=30)
        #response['data']['tempo'] = 0

        # Check if the response contains an error
        if response.status_code >= 400:
            print("Error:", response.json())  # Assuming the error is in JSON format

        return response.json()['data']
    except requests.exceptions.RequestException as e:
        # Print the exception error if the request fails
        print("Request failed with error:", str(e))

def process_workout_excel_data():
    print("Processing workout excel data...")

    # Load Excel data
    file_path = input("Name of file to translate: ").strip()
    try:
        workout_info_df = pd.read_excel(file_path)
    except FileNotFoundError:
        print("Error: Excel file not found. Please check the file path.")
        return
    except Exception as e:
        print(f"Error: Failed to load Excel file: {e}")
        return
    
    print("Getting start positions for each workout in Excel sheet...")
    # Find all occurrences of "Status" and their positions
    workout_start_positions = collections.deque([])
    col_index = workout_info_df.columns.get_loc("Workouts")
    for row_index, row in workout_info_df.iterrows():
        if row["Workouts"] == "Status":
            workout_start_positions.append((row_index, col_index))

    #print("Workout start positions: ", workout_start_positions)

    # Find all occurrences of "Section name" and their positions
    section_start_positions = collections.deque([])
    col_index = workout_info_df.columns.get_loc("Sections")
    for row_index, row in workout_info_df.iterrows():
        if row["Sections"] == "Section name":
            section_start_positions.append((row_index, col_index))

    #print("Section start positions: ", section_start_positions)

    # Find all occurrences of "Superset num exercises" and their positions
    superset_start_positions = collections.deque([])
    col_index = workout_info_df.columns.get_loc("Supersets")
    for row_index, row in workout_info_df.iterrows():
        if row["Supersets"] == "Superset num exercises":
            superset_start_positions.append((row_index, col_index))

    #print("Superset start positions: ", superset_start_positions)

    # Find all occurrences of "Exercise name" and their positions
    exercise_start_positions = collections.deque([])
    col_index = workout_info_df.columns.get_loc("Exercises")
    for row_index, row in workout_info_df.iterrows():
        if row["Exercises"] == "Exercise name":
            exercise_start_positions.append((row_index, col_index))

    #print("Exercise start positions: ", exercise_start_positions)

    # Find all occurrences of "Set reps" and their positions
    set_start_positions = collections.deque([])
    col_index = workout_info_df.columns.get_loc("Sets")
    for row_index, row in workout_info_df.iterrows():
        if "set reps" in str(row["Sets"]).lower():
            set_start_positions.append((row_index, col_index))

    #print("Set start positions: ", set_start_positions)

    workouts_info = []

    # Go through workout data
    for num_workout in range(len(workout_start_positions)):
        workout_info = {}
        w_row, w_col = workout_start_positions.popleft()
        print(f"Workout {num_workout + 1}...")
        workout_info["status"] = workout_info_df.iloc[w_row + 1, w_col]
        workout_info["title"] = workout_info_df.iloc[w_row + 1, w_col + 1]
        workout_info["description"] = workout_info_df.iloc[w_row + 1, w_col + 2]
        workout_info["num_sections"] = workout_info_df.iloc[w_row + 1, w_col + 3]
        workout_info["sections"] = []

        # Go through section data
        for num_section in range(workout_info["num_sections"]):
            section_info = {}
            s_row, s_col = section_start_positions.popleft()
            print(f"\tSection {num_section + 1}...")
            section_info["section_name"] = workout_info_df.iloc[s_row + 1, s_col]
            section_info["section_format"] = workout_info_df.iloc[s_row + 1, s_col + 1]
            section_info["section_type"] = workout_info_df.iloc[s_row + 1, s_col + 2]
            section_info["section_note"] = workout_info_df.iloc[s_row + 1, s_col + 3]
            section_info["section_duration"] = workout_info_df.iloc[s_row + 1, s_col + 4]
            section_info["num_supersets"] = workout_info_df.iloc[s_row + 1, s_col + 5]
            section_info["supersets"] = []

            # Go through superset data
            for num_superset in range(section_info["num_supersets"]):
                superset_info = {}
                e_row, e_col = superset_start_positions.popleft()
                print(f"\t\tSuperset {num_superset + 1}...")
                superset_info["num_exercises"] = workout_info_df.iloc[e_row + 1, e_col]
                superset_info["exercises"] = []

                # Go through exercise data
                for num_exercise in range(superset_info["num_exercises"]):
                    exercise_info = {}
                    e_row, e_col = exercise_start_positions.popleft()
                    print(f"\t\t\tExercise {num_exercise + 1}...")
                    exercise_info["exercise_name"] = workout_info_df.iloc[e_row + 1, e_col]
                    exercise_info["exercise_note"] = workout_info_df.iloc[e_row + 1, e_col + 1]
                    exercise_info["exercise_tempo"] = workout_info_df.iloc[e_row + 1, e_col + 2]
                    exercise_info["each_side"] = workout_info_df.iloc[e_row + 1, e_col + 3]
                    exercise_info["num_sets"] = workout_info_df.iloc[e_row + 1, e_col + 4]
                    exercise_info["sets"] = []

                    # Go through set data
                    for num_set in range(exercise_info["num_sets"]):
                        sets_info = {}
                        set_row, set_col = set_start_positions.popleft()
                        print(f"\t\t\t\tTraining set {num_set + 1}...")
                        sets_info["set_reps"] = workout_info_df.iloc[set_row + 1, set_col]
                        sets_info["set_rest"] = workout_info_df.iloc[set_row + 1, set_col + 1]
                        sets_info["set_duration"] = workout_info_df.iloc[set_row + 1, set_col + 2]
                        exercise_info["sets"].append(sets_info)
                    superset_info["exercises"].append(exercise_info)
                section_info["supersets"].append(superset_info)
            workout_info["sections"].append(section_info)
        workouts_info.append(workout_info)

    return workouts_info

# Create payload functions

def create_sets_list(sets_info, section_format):
    sets_list = []
    for set_info in sets_info:
        # set info
        info = {}

        if section_format == "regular":
            info["reps"] = {"value": set_info.get("set_reps", "")}
            info["rest"] = {"value": set_info.get("set_rest", "")}
        
        if section_format == "interval":
            info["duration"] = {"value": set_info.get("set_duration", "")} # it is there but invisible to user
            info["rest"] = {"value": set_info.get("set_rest", "")}

        # EMOM adjustment
        if section_format == "emom":
            info["reps"] = {"value": set_info.get("set_reps", "")}
            info["duration"] = {"value": "60"} # it is there but invisible to user
            info["rest"] = {"value": "0"}
            
        # add set info to list
        sets_list.append(info)

    return sets_list

def get_exercise_id(exercise_name, session, access_token):

    # Get exercise id of exercise
    exercise_id = ""
    everfit_exercises_data = get_exercises(session, access_token)
    for exercise_data in everfit_exercises_data:
        if exercise_data['title'].strip().lower() == exercise_name.strip().lower():
            exercise_id = exercise_data['_id']
            break

    # empty string if id not found
    if exercise_id == "":
        print(f"Exercise '{exercise_name}' not found in Everfit application.")

    return exercise_id

def create_supersets_list(supersets_info, section_format, session, headers, access_token):
    supersets_list = []
    for superset_info in supersets_info:
        # superset info
        info = {
            "supersets": create_exercises_list(superset_info["exercises"], section_format, session, headers, access_token)
        }

        # add superset info to list
        supersets_list.append(info)

    return supersets_list

def create_exercises_list(exercises_info, section_format, session, headers, access_token):
    exercises_list = []
    for exercise_info in exercises_info:
        # get exercise id
        exercise_id = get_exercise_id(exercise_info.get("exercise_name", ""), session, access_token)
        
        # exercise info
        info = {
                "alternatives": [],
                "each_side": True if exercise_info["each_side"] == 1 else False,
                "exercise": exercise_id,
                "exercise_instance": get_individual_exercise_data(exercise_id, session, headers),
                "note": exercise_info["exercise_note"],
                "tempo": exercise_info["exercise_tempo"],
                "training_sets": create_sets_list(exercise_info.get("sets", []), section_format)
        }

        # add exercise info to list
        exercises_list.append(info)

    return exercises_list

def create_section_list(sections_info, session, headers, access_token):
    section_list = []
    for section_info in sections_info:
        section_format = section_info["section_format"].lower()
        # section info
        info = {
                    "attachments": [],
                    "exercises": create_supersets_list(section_info["supersets"], section_format, session, headers, access_token),
                    "format": section_format, 
                    "note": section_info["section_note"],
                    "time": "", 
                    "title": section_info["section_name"],
                    "type": filter_section_type(section_info["section_type"])
        }
        
        # add time duration if format is 'amrap'
        if section_info["section_format"].lower() == 'amrap':
            info["time"] = min_to_seconds(section_info.get("amrap_duration", 30))
        # add 'round' key if format is 'timed'
        elif section_info["section_format"].lower() == 'timed':
            info["round"] = section_info.get("timed_rounds", 1)

        # adjust EMOM format
        if section_format == 'emom':
            info["format"] = "interval"

        # add section info to list
        section_list.append(info)

    return section_list

def create_workout_payload(workout_info, session, headers, access_token):

    payload = {
        "author": "666c67f6c98eb80026f047c9",
        "title": workout_info["title"],
        "description": workout_info["description"],
        "timezone": "America/Los_Angeles",
        "is_generated_by_ai": False,
        "sections": create_section_list(workout_info["sections"], session, headers, access_token),
        "share": 0,
        "tags": []
    }

    return payload

def main():
    print("workouts.py...")

    email = input("Enter your email: ").strip()
    password = getpass.getpass("Enter your password: ").strip()

    session = requests.Session()

    access_token = login(session, email, password)

    workout_information = process_workout_excel_data()

    # Define headers
    headers = {
        "Agent": "react",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-Access-Token": access_token,  # Ensure this token is dynamically set
        "X-App-Type": "web-coach",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",  # Match the language header
        "Referer": "https://app.everfit.io/",
        "Origin": "https://app.everfit.io",
        "Cache-Control": "no-cache",
        "Timezone": "America/Los_Angeles",  # Add the Timezone header if required
        "Sec-CH-UA": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',  # Include Sec-CH-UA header
        "Sec-CH-UA-Mobile": "?0",  # Include Sec-CH-UA-Mobile header
        "Sec-CH-UA-Platform": '"macOS"',  # Include Sec-CH-UA-Platform header
        "Sec-Fetch-Dest": "empty",  # Include Sec-Fetch-Dest header
        "Sec-Fetch-Mode": "cors",  # Include Sec-Fetch-Mode header
        "Sec-Fetch-Site": "same-site",  # Include Sec-Fetch-Site header
    }

    # Define urls
    url = "https://api-prod3.everfit.io/api/workout/v2/add"

    for workout in workout_information:
        # continue if status is not 1
        if workout['status'] != 1:
            print(f"Skipping workout {workout['title']} (status is not 1)")
            continue
        print(f"Creating payload for {workout['title']}...")
        payload = {
            "author": "666c67f6c98eb80026f047c9",
            "conversion_id": None,
            "title": workout['title'],
            "description": workout['description'],
            "timezone": "America/Los_Angeles",
            "is_generated_by_ai": False,
            "sections": create_section_list(workout['sections'], session, headers, access_token),
            "share": 0,
            "tags": []
        }
        
        try:
            print(f"Uploading {workout['title']}...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
                
            # Check if the response contains an error
            if response.status_code >= 400:
                print("Request Failed:")
                """print("Request Headers:", response.request.headers)
                print("Request Payload:", payload)
                print("Response Status Code:", response.status_code)
                print("Response Headers:", response.headers)"""
                print("Response Body:", response.text)
            else:
                print("Successfully added workout.")
        except requests.exceptions.RequestException as e:
            # Print the exception error if the request fails
            print("Request failed with error:", str(e))
    
    session.close()

if __name__ == "__main__":
    main()