from api import *
from config import *
from utils import *

import requests
import getpass
import pandas as pd
import json

def get_tags_from_exercise_data(tag_list):
    tags = []
    for tag in tag_list:
        tags.append(tag['name'])
    return tags

# Function to add exercise_info data to the corresponding row based on column matching
def add_exercises_to_excel(exercise_df, exercise_info_list, start_row_index):
    # Loop through each exercise_info
    for idx, exercise_info in enumerate(exercise_info_list):
        tags = exercise_info.pop('Tags', [])
        cur_row_index = start_row_index + idx
        col_names = exercise_df.columns.tolist()
        # Adds up to 'Video link' for each exercise
        for key, val in exercise_info.items():
            for col_name in col_names:
                if key.lower() == col_name.lower():
                    exercise_df.loc[cur_row_index, col_name] = val
                    break   
        # Add tags
        video_link_index = col_names.index("Video link") 
        skill_names_or_equipment = ["SKILL NAME 1", "SKILL NAME 2", "SKILL NAME 3", "EQUIPMENT 1", "EQUIPMENT 2", "EQUIPMENT 3", "EQUIPMENT 4"]
        # go through each column, if there is a tag == column, put 1 else 0
        for col_name in col_names[video_link_index+1:]:
            # leave blank if a skill name or equipment
            if col_name in skill_names_or_equipment:
                exercise_df.loc[cur_row_index, col_name] = ""
            elif any(tag.lower() == col_name.lower() for tag in tags):
                exercise_df.loc[cur_row_index, col_name] = 1
            else:
                exercise_df.loc[cur_row_index, col_name] = 0   
        print(f"Successfully added exercise {exercise_info['EXERCISE NAME']} to dataframe.")     
    
    return exercise_df

def fetch_individual_exercise_details(response, session, headers):
    # Used for getting each individual exercise details (base + exercise id)
    base_url = "https://api-prod3.everfit.io/api/exercise/detail/"

    # Data to return
    data = []
    total_exercises = len(response['data'])
    i = 1

    for exercise in reversed(response['data'][:]):
        # get id and request details
        detail_url = base_url + exercise['_id']
        detail_response = session.get(detail_url, headers=headers)
        if detail_response.ok:
            exercise_data = detail_response.json()['data']

            print(f"Got exercise {exercise_data['title']} details successfully.")
            print(f"{(i/total_exercises)*100}%...")

            exercise_info = {
                "EXERCISE NAME": exercise_data.get('title', ""),
                "VIDEO STATUS": 2,
                "Description": 0 if not exercise_data.get('instructions', []) else 1,
                "Modality": exercise_data.get('modality', {}).get('title', ""),
                "Muscle group": exercise_data['muscle_groups'][0]['muscle_group']['title'] if len(exercise_data['muscle_groups']) > 0 else "",
                "Muscle group 2": exercise_data['muscle_groups'][1]['muscle_group']['title'] if len(exercise_data['muscle_groups']) > 1 else "",
                "Muscle group 3": exercise_data['muscle_groups'][2]['muscle_group']['title'] if len(exercise_data['muscle_groups']) > 2 else "",
                "Movement pattern 1": exercise_data['movement_patterns'][0]['movement_pattern']['title'] if len(exercise_data['movement_patterns']) > 0 else "",
                "Movement pattern 2": exercise_data['movement_patterns'][1]['movement_pattern']['title'] if len(exercise_data['movement_patterns']) > 1 else "",
                "Movement pattern 3": exercise_data['movement_patterns'][2]['movement_pattern']['title'] if len(exercise_data['movement_patterns']) > 2 else "",
                "Category": exercise_data.get('category_type_name', ""),
                "Tracking fields": ', '.join([REVERSE_TRACKING_FIELDS_MAP.get(field_id, 'Unknown').capitalize() for field_id in exercise_data['fields'][:-1]]),
                "Instructions": '\n'.join(exercise_data.get('instructions', [])),
                "Video link": exercise_data.get('videoLink', ""),
                "Tags": get_tags_from_exercise_data(exercise_data.get('tags', []))
            }
            i += 1
            data.append(exercise_info)
        else:
            print("Failed to retrieve exercise details.")

    return data

def main():
    # Start session
    session = requests.Session()

    # Define email and password
    email = input("Enter your email: ")
    password = getpass.getpass("Enter your password: ")

    # Log in and get access token
    access_token = login(session, email, password)
    if not access_token:
        print("Exiting due to failed login.")

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "x-access-token": access_token,
        "x-app-type": "web-coach",
    }

    # Gets all exercises in Everfit exercise library
    response = get_exercises(session, access_token)

    # Create data from individual exercise details
    data = fetch_individual_exercise_details(response, session, headers)

    # Load existing blank template Excel sheet
    file_path = 'BlankExerciseData.xlsx' 
    exercise_df = pd.read_excel(file_path)

    # Call the function to insert data into the appropriate row
    start_index = exercise_df[exercise_df.iloc[:, 0] == 'EXERCISE NAME'].index[0] + 1
    updated_df = add_exercises_to_excel(exercise_df, data, start_index)

    # Save the updated DataFrame back to Excel
    output_file = 'UpdatedExerciseSheet.xlsx'
    updated_df.to_excel(output_file, index=False)

    print(f"Data has been written to {output_file}")

if __name__ == "__main__":
    main()