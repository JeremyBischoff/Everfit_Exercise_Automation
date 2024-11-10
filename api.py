import requests

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

    # Validate inputs
    if not isinstance(email, str) or not email.strip():
        raise ValueError("Email must be a non-empty string.")
    if not isinstance(password, str) or not password.strip():
        raise ValueError("Password must be a non-empty string.")

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
    try:
        response = session.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Login request failed: {e}")
        return None
    
    try:
        data = response.json()
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None
    
    access_token = data.get('token')
    if access_token:
        print("Logged in successfully.")
        return access_token
    else:
        print("Login failed: No token found in response.")
        return None
    
def put_exercise(session, access_token, exercise_id, payload):

    # Validate inputs
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary.")
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Access token must be a non-empty string.")    
    
    # Define url
    url = "https://api-prod3.everfit.io/api/exercise/update/" + exercise_id

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "X-Access-Token": access_token,
        "X-App-Type": "web-coach",
    }

    # Send the PUT request to update the exercise
    try:
        response = session.put(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to update exercise: {e}")
        return None

    try:
        data = response.json()
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None

    return data

def post_exercise(session, payload, access_token):
    """
    Sends a POST request to the Everfit API to add a new exercise.

    Args:
        session (requests.Session): The active session used to make the request.
        payload (dict): The exercise data to be added.
        access_token (str): The access token for authenticating the request.

    Returns:
        Response: The response object from the POST request.
    """

    # Validate inputs
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary.")
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Access token must be a non-empty string.")

    # Define url
    url = "https://api-prod3.everfit.io/api/exercise/add"

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "X-Access-Token": access_token,
        "X-App-Type": "web-coach",
    }

    # Send the POST request to add the exercise
    try:
        response = session.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to add exercise: {e}")
        return None

    try:
        data = response.json()
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None

    return data

def get_exercises(session, access_token):
    """
    Retrieves a list of exercises from the Everfit API.

    Args:
        session (requests.Session): The active session used to make the request.
        access_token (str): The access token for authenticating the request.

    Returns:
        dict: The JSON response containing the exercises if successful, or None if the request fails.
    """

    # Validate access_token
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Access token must be a non-empty string.")

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
    try:
        initial_response = session.post(url, json=payload, headers=headers, timeout=30)
        initial_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve exercises: {e}")
        return None
    
    try:
        initial_data = initial_response.json()
        total_exercises = initial_data.get('total', 0)
        if not isinstance(total_exercises, int) or total_exercises <= 0:
            print("No exercises found.")
            return None
    except ValueError as e:
        print(f"Failed to parse initial response JSON: {e}")
        return None

    payload["per_page"] = total_exercises

    # Send request to get all exercises
    try:
        response = session.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve exercises: {e}")
        return None

    try:
        data = response.json()
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None
    
    return data['data']

def get_tag_list(session, access_token):
    """
    Retrieves the full list of tags from the Everfit API.

    Args:
        session (requests.Session): The active session used to make the request.
        access_token (str): The access token for authenticating the request.

    Returns:
        list: A list of tags if successful, or None if the request fails.
    """

    # Validate access_token
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Access token must be a non-empty string.")

    # Define url
    base_url = "https://api-prod3.everfit.io/api/tag/get-list-tag-by-team"

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "x-access-token": access_token,
        "x-app-type": "web-coach",
    }

    # First request to get total number of tags
    params = {
        "sorter": "name",
        "per_page": 1,  # Get minimal data to retrieve total
        "page": 1,
        "sort": 1,
        "text_search": "",
        "type": 1
    }

    try:
        response = session.get(base_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve tags: {e}")
        return None
    
    try:
        data = response.json()
        total_tags = data.get('data', {}).get('total', 0)
        if not isinstance(total_tags, int) or total_tags <= 0:
            print("No tags found.")
            return []
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None
    
    # Second request to get all tags
    params['per_page'] = total_tags

    try:
        tag_list_response = session.get(base_url, headers=headers, params=params, timeout=30)
        tag_list_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the full list of tags: {e}")
        return None

    try:
        tag_data = tag_list_response.json()
        tag_list = tag_data.get('data', {}).get('data', [])
    except ValueError as e:
        print(f"Failed to parse tag list JSON: {e}")
        return None

    return tag_list
    
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

    # Validate inputs
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Access token must be a non-empty string.")
    if not isinstance(tag, str) or not tag.strip():
        raise ValueError("Tag name must be a non-empty string.")

    # Define url
    url = "https://api-prod3.everfit.io/api/tag"

    # Define headers
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "x-access-token": access_token,
        "x-app-type": "web-coach",
    }

    # Define payload
    payload = {
        "name": tag.strip(),
        "type": 1
    }

    # Send a POST request to the url to make a new tag
    try:
        response = session.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to create new tag '{tag}': {e}")
        return None

    try:
        data = response.json()
        tag_data = data.get('data', {})
        tag_id = tag_data.get('_id')
        if not tag_id:
            print(f"Failed to get new tag ID from response.")
            return None
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None

    return tag_id