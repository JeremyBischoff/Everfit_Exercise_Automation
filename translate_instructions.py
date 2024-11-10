from api import *
from utils import *
from config import *

import deepl
import pandas as pd
import requests
import getpass

# Ruben types instruction into spanish -> runs this command to translate instructions -> uploads to Everfit with main.py command
def exercise_instructions_ES_to_EN_and_ES():

    auth_key = "b6bc67c9-a89b-46c4-934f-3e19d8ba3e26:fx"
    translator = deepl.Translator(auth_key)

    # Load Excel data
    file_path = input("Name of file to translate: ").strip()
    try:
        exercise_df = pd.read_excel(file_path)
    except FileNotFoundError:
        print("Error: Excel file not found. Please check the file path.")
        return
    except Exception as e:
        print(f"Error: Failed to load Excel file: {e}")
        return

    # Validate necessary columns
    if "EXERCISE NAME" not in exercise_df.columns.tolist() or "Instructions" not in exercise_df.columns.tolist():
        print("Error: Required columns ('EXERCISE NAME' and 'instructions') are missing in the Excel file.")
        return

    """
    # Optional: Get start and end exercise to translate instructions (must be contingent)
    start_exercise_name = input("Start exercise name to translate (leave blank to start from beginning): ").strip()
    end_exercise_name = input("End exercise name to translate (leave blank to go until end): ").strip()

    # Start at specific start index from where you want to change
    try:
        # Find the starting index based on the specified exercise name
        if start_exercise_name == "":
            start_index = exercise_df.loc[exercise_df["EXERCISE NAME"].str.strip() == "EXERCISE NAME"].index[0] + 1
        else:
            start_index = exercise_df.loc[exercise_df["EXERCISE NAME"].str.strip().str.lower() == start_exercise_name.lower()].index[0]
    except IndexError:
        print(f"Exercise '{start_exercise_name}' not found in the Excel file.")
        return
    
    try:
        # Find the end index based on the specified exercise name
        if end_exercise_name == "":
            end_index = len(exercise_df)-1
        else:
            end_index = exercise_df.loc[exercise_df["EXERCISE NAME"].str.strip().str.lower() == end_exercise_name.lower()].index[0]
    except IndexError:
        print(f"Exercise '{end_exercise_name}' not found in the Excel file.")
        return
    """

    # To translate full Excel sheet
    start_index = exercise_df.loc[exercise_df["EXERCISE NAME"].str.strip() == "EXERCISE NAME"].index[0] + 1
    end_index = len(exercise_df)-1

    # Get the full exercises list of the exercises we want to modify
    exercises_list = get_exercises_list(start_index, exercise_df, post_exercises_flag=False, end_index=end_index)
    if not exercises_list:
        print("No exercises found to process.")
        return
    
    # Translates instructions for each exercise if necessary
    for i, exercise_info in enumerate(exercises_list):
        # Initializes variables
        instructions = [] if pd.isna(exercise_info["instructions"]) else safe_str(exercise_info["instructions"]).split('\n')    
        translated_instructions = [""] * len(instructions)
        translatedAlready = False
        emptyInstruction = False

        for ind, instruction in enumerate(instructions):
            # Check if already translated:
            if '|' in instruction:
                translatedAlready = True
                break
            # Check if blank
            if instruction == "":
                emptyInstruction = True
                break
            # Translate the instruction and format as "English | Spanish"
            try:
                print(f"Translating instructions for {exercise_info['exercise_name']}...")
                EN_translation = translator.translate_text(safe_str(instruction), target_lang="EN-US").text
                translated_instructions[ind] = EN_translation + " | " + instruction
            except DeepLException as e:
                print(f"Error: Failed to translate instruction for '{exercise_info.get('exercise_name', 'Unknown')}': {e}")
                translated_instructions[ind] = instruction  # Keep original instruction on failure
        # Breaks if already translated
        if translatedAlready:
            print(f"{exercise_info['exercise_name']} already has translated instructions.")
            continue
        # Breaks if empty instructions
        elif emptyInstruction:
            print(f"{exercise_info['exercise_name']} has blank instructions.")
            continue
        # Updates translated instructions to DataFrame
        exercise_df.at[start_index + i, "Instructions"] = "\n".join(translated_instructions)

    return exercise_df

def main():

    # Changes 
    translated_df = exercise_instructions_ES_to_EN_and_ES()

    # Save the updated DataFrame back to Excel
    output_file = 'TranslatedExerciseData.xlsx'
    try:
        translated_df.to_excel(output_file, index=False)
        print(f"Data has been written to {output_file}")
    except Exception as e:
        print(f"Error: Failed to save the Excel file: {e}")
    
if __name__ == "__main__":
    main()