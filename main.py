from utils import *
from api import *
from config import *

import pandas as pd
import requests
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

    # Start a session
    session = requests.Session()

    try:
        # Load Excel data
        file_path = 'ExerciseData.xlsx'
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

        # Get the list of exercises
        exercises_list = get_exercises_list(start_index, exercise_df)
        if not exercises_list:
            print("No exercises found to process.")
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

        # Add each exercise to Everfit
        for exercise_info in exercises_list:
            exercise_name = exercise_info.get('exercise_name', 'Unknown')
            try:
                payload = get_payload(session, access_token, exercise_info, exercise_df)
            except Exception as e:
                print(f"Failed to generate payload for exercise '{exercise_name}': {e}")
                continue

            try:
                add_exercise_response = add_exercise(session, payload, access_token)
            except Exception as e:
                print(f"Failed to add exercise '{exercise_name}': {e}")
                continue

            if not add_exercise_response:
                print(f"Failed to add exercise '{exercise_name}'. No response received.")
                print(f"Payload: {payload}")
                continue
            else:
                print(f"Exercise '{exercise_name}' added successfully.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the session is closed
        session.close()

if __name__ == "__main__":
    main()