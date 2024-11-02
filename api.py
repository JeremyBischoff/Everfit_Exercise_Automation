def login(session, email, password):
    """
    Logs into the Everfit API using the provided email and password and retrieves an access token.

    Args:
        session (requests.Session): The active session used to make the login request.
        email (str): The user's email address for login.
        password (str): The user's password for login.

    Returns:
        str: The access token if login is successful, or None if login fails.
    """

    # Define url
    url = "https://api-prod3.everfit.io/api/auth/login_lite"

    # Define payload
    payload = {
        "email": email,
        "password": password,
        "agent": "react",
    }

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "x-app-type": "web-coach",
    }

    # Send a POST request to log in
    response = session.post(url, json=payload, headers=headers)
    if response.ok:
        print("Logged in successfully.")
        data = response.json()
        access_token = data.get('token')
        return access_token
    else:
        print("Login failed:", response.status_code, response.text)
        return None
    
def add_exercise(session, payload, access_token):
    """
    Sends a POST request to the Everfit API to add a new exercise.

    Args:
        session (requests.Session): The active session used to make the request.
        payload (dict): The exercise data to be added.
        access_token (str): The access token for authenticating the request.

    Returns:
        Response: The response object from the POST request.
    """

    # Define url
    url = "https://api-prod3.everfit.io/api/exercise/add"

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "X-Access-Token": access_token,
        "X-App-Type": "web-coach",
    }

    # Send the POST request to add the exercise
    response = session.post(url, json=payload, headers=headers)

    return response

def get_exercises(session, access_token):
    """
    Retrieves a list of exercises from the Everfit API.

    Args:
        session (requests.Session): The active session used to make the request.
        access_token (str): The access token for authenticating the request.

    Returns:
        dict: The JSON response containing the exercises if successful, or None if the request fails.
    """

    total_exercises = 50

    # Define urls
    url = "https://api-prod3.everfit.io/api/exercise/search_filter_library"

    # Define payload
    payload = {
        "body_part": [],
        "category_type": [],
        "equipments": [],
        "from": [False, True], # [False, True] makes it only the Custom Exercises
        "modalities": [],
        "movement_patterns": [],
        "muscle_groups": [],
        "page": 1,
        "per_page": total_exercises,
        "q": "",
        "sort": -1,
        "sorter": "last_interacted",
        "tags": [],
        "video_only": False
    }

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "x-access-token": access_token,
        "x-app-type": "web-coach",
    }

    # Send a POST request to the url    
    initial_response = session.post(url, json=payload, headers=headers)
    if initial_response.ok:
        print("Exercises retrieved successfully.")
        total_exercises = initial_response.json()['total']
        print("Total number of exercises:", total_exercises)
        payload["per_page"] = total_exercises
        response = session.post(url, json=payload, headers=headers)
        return response.json()
    else:
        print("Failed to retrieve exercises:", initial_response.status_code, initial_response.text)
        return None

def get_tag_list(session, access_token):
    """
    Retrieves the full list of tags from the Everfit API.

    Args:
        session (requests.Session): The active session used to make the request.
        access_token (str): The access token for authenticating the request.

    Returns:
        list: A list of tags if successful, or None if the request fails.
    """

    # Define url
    default_per_page = 20
    url = "https://api-prod3.everfit.io/api/tag/get-list-tag-by-team?sorter=name&per_page={per_page}&page=1&sort=1&text_search=&type=1"

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "x-access-token": access_token,
        "x-app-type": "web-coach",
    }

    # Send a POST request to the url to get total number of tags
    response = session.get(url.format(per_page=default_per_page), headers=headers)
    if response.ok:
        total_tags = response.json()['data']['total']  
        # Send another POST request to the url to get the tags
        tag_list_response = session.get(url.format(per_page=total_tags), headers=headers)
        if tag_list_response.ok:
            tag_list = tag_list_response.json()['data']['data']
            return tag_list
        else:
            print("Failed to retrieve the full list of tags:", tag_list_response.status_code, tag_list_response.text)
            return None
    else:
        print("Failed to retrieve tags:", response.status_code, response.text)
        return None
    
def create_new_tag_id(session, access_token, tag):
    """
    Creates a new tag in the Everfit API and returns the newly created tag's ID.

    Args:
        session (requests.Session): The active session used to make the request.
        access_token (str): The access token for authenticating the request.
        tag (str): The name of the new tag to be created.

    Returns:
        str: The ID of the newly created tag if successful, or None if the request fails.
    """

    # Define url
    url = "https://api-prod3.everfit.io/api/tag/"

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "x-access-token": access_token,
        "x-app-type": "web-coach",
    }

    # Define payload
    payload = {
        "name": tag,
        "type": 1
    }

    # Send a POST request to the url to make a new tag
    response = session.post(url, json=payload, headers=headers)
    if response.ok:
        data = response.json()['data']
        return data["_id"]
    else:
        print("Failed to make new tag:", response.status_code, response.text)
        return None