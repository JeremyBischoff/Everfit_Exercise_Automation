from utils import *
from api import *
from config import *

import pandas as pd
import requests
import getpass

# Steps:
# 1. Write out exercises and exercise information in ExcelData.xlsx (
#   * 1 in "VIDEO STATUS" to add exercise, 3 to update exercise
# 2. Translate instructions from Spanish to English with translate_instructions.py
# 3. Add/update exercises from ExcelData.xlsx to Everfit application with main.py

def main():
    """
    Main function that coordinates the process of reading exercise data from an Excel file,
    logging into the Everfit API, and uploading exercises.

    Steps:
    1. Loads exercise data from 'ExerciseData.xlsx'.
    2. Logs into the Everfit API using provided credentials and retrieves an access token.
    3. Constructs a list of exercises from the loaded data.
    4. Uploads the exercises from the list to the Everfit API using the generated payload.
    5. Handles server load by adding a delay between uploads and ensures session is properly closed.
    """

    # Start a session
    session = requests.Session()

    try:
        # Load Excel data
        file_path = input("Name of file: ").strip()
        try:
            exercise_df = pd.read_excel(file_path)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return
        except Exception as e:
            print(f"Error reading '{file_path}': {e}")
            return

        # Find the start index of exercises
        try:
            start_index = exercise_df[exercise_df.iloc[:, 0] == 'EXERCISE NAME'].index[0] + 1
        except IndexError:
            print("Error: 'EXERCISE NAME' not found in the first column of the Excel file.")
            return
        except Exception as e:
            print(f"Error processing Excel data: {e}")
            return

        # Get user credentials
        try:
            email = input("Enter your email: ").strip()
            if not email:
                print("Email cannot be empty.")
                return
            password = getpass.getpass("Enter your password: ").strip()
            if not password:
                print("Password cannot be empty.")
                return
        except Exception as e:
            print(f"Error getting user input: {e}")
            return

        # Log in to the API
        access_token = login(session, email, password)
        if not access_token:
            print("Exiting due to failed login.")
            return
        else:
            print("Access token obtained.")

        # Get the list of POST exercises
        post_exercises_list = get_exercises_list(start_index, exercise_df, post_exercises_flag=True)
        if not post_exercises_list:
            print("No exercises found to add.")

        # POST each exercise to Everfit
        for exercise_info in post_exercises_list:
            # Get payload to add exercise
            exercise_name = exercise_info.get('exercise_name', 'Unknown')
            try:
                payload = get_payload(session, access_token, exercise_info, exercise_df)
            except Exception as e:
                print(f"Failed to generate payload for exercise '{exercise_name}': {e}")
                continue
            # Network call to add exercise
            try:
                post_exercise_response = post_exercise(session, payload, access_token)
            except Exception as e:
                print(f"Failed to add exercise '{exercise_name}': {e}")
                continue
            # Debugging purposes
            if not post_exercise_response:
                print(f"Failed to add exercise '{exercise_name}'. No response received.")
                print(f"Payload: {payload}")
                continue
            else:
                print(f"Exercise '{exercise_name}' added successfully.")

        # Get the list of PUT exercises
        put_exercises_list = get_exercises_list(start_index, exercise_df, post_exercises_flag=False, put_exercises_flag=True)
        if not put_exercises_list:
            print("No exercises found to update.")

        # PUT each exercise to Everfit
        for exercise_info in put_exercises_list:
            # Get payload to update exercise
            exercise_name = exercise_info.get('exercise_name', 'Unknown')
            try:
                payload = get_payload(session, access_token, exercise_info, exercise_df)
            except Exception as e:
                print(f"Failed to generate payload for exercise '{exercise_name}': {e}")
                continue
            # Get exercise id of exercise
            exercise_id = ""
            everfit_exercises_data = get_exercises(session, access_token)
            for exercise_data in everfit_exercises_data:
                if exercise_data['title'].strip().lower() == payload['title'].strip().lower():
                    exercise_id = exercise_data['_id']
                    break
            if exercise_id == "":
                print(f"Exercise '{exercise_name}' not found in Everfit application. Please add the exercise before attempting to update it.")
                continue
            # Network call to update exercise
            try:
                put_exercise_response = put_exercise(session, access_token, exercise_id, payload)
            except Exception as e:
                print(f"Failed to update exercise '{exercise_name}': {e}")
                continue
            # Debugging purposes
            if not put_exercise_response:
                print(f"Failed to update exercise '{exercise_name}'. No response received.")
                print(f"Payload: {payload}")
                continue
            else:
                print(f"Exercise '{exercise_name}' updated successfully.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()