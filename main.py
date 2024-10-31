from utils import *
from api import *
from config import *

import pandas as pd
import requests
import time
import getpass

def main():
    """
    Main function that coordinates the process of reading exercise data from an Excel file,
    logging into the Everfit API, and uploading exercises.

    Steps:
    1. Loads exercise data from 'ExerciseData.xlsx'.
    2. Logs into the Everfit API using provided credentials and retrieves an access token.
    3. Constructs a list of exercises from the loaded data.
    4. Uploads the last 3 exercises from the list to the Everfit API using the generated payload.
    5. Handles server load by adding a delay between uploads and ensures session is properly closed.
    """

    # Load excel data in
    file_path = 'ExerciseData.xlsx'
    exercise_df = pd.read_excel(file_path, sheet_name='DATA Exercises')

    # Define start index (first cell under 'EXERCISE NAME' in first column) and get exercise list
    start_index = exercise_df[exercise_df.iloc[:, 0] == 'EXERCISE NAME'].index[0] + 1
    exercises_list = get_exercises_list(start_index, exercise_df)

    # Start session
    session = requests.Session()

    # Define email and password
    email = input("Enter your email: ")
    password = getpass.getpass("Enter your password: ")

    # Log in and get access token
    access_token = login(session, email, password)
    if not access_token:
        print("Exiting due to failed login.")
        return
    else:
        print("Access token obtained.")

    # Add each exercise to Everfit
    for exercise_info in exercises_list[:3]:
        payload = get_payload(session, access_token, exercise_info, exercise_df)
        add_exercise_response = add_exercise(session, payload, access_token)
        if not add_exercise_response:
            print(f"Failed to add exercise {exercise_info['exercise_name']}")
            print(add_exercise_response.json())
            print(add_exercise_response.status_code)
            print(f"Payload: {payload}")
        else:
            print(f"Exercise {exercise_info['exercise_name']} added successfully.")
        # Sleep to not overload server
        #time.sleep(1)

    # Close session
    session.close()

if __name__ == "__main__":
    main()