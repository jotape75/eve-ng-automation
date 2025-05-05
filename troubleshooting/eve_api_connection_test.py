"""
eve_api.py

This script interacts with the EVE-NG API to authenticate a user and retrieve data from a specified endpoint. 
It demonstrates how to use Python's `requests` library to make HTTP requests and handle JSON responses.

Functions:
-----------
1. get_data(data):
    - Accepts a dictionary and pretty-prints it as a JSON-formatted string.
    - Useful for debugging and visualizing API responses.

2. user_auth():
    - Authenticates the user with the EVE-NG API using a POST request.
    - Returns the response object containing authentication cookies if successful.
    - Exits the script if authentication fails.

Main Execution:
---------------
- Authenticates the user with the EVE-NG API.
- Makes a GET request to retrieve network data from the specified lab (`Ansiblelab.unl`).
- Pretty-prints the retrieved data using the `get_data` function.

Dependencies:
-------------
- requests: For making HTTP requests.
- json: For handling JSON data.
- csv: (Imported but not used in this script.)
- pprint: For pretty-printing JSON responses.

Usage:
------
Run the script directly to authenticate with the EVE-NG API and retrieve network data:
    python eve_api.py

Note:
-----
Ensure the EVE-NG server is running and accessible at the specified URL.
Update the `username`, `password`, and url and `data_url` variables as needed for your environment.
"""

import requests # Import the requests module.
import json # Import the json module.
import csv # Import the csv module.
from pprint import pprint # Import the pprint module for pretty-printing.

def get_data(data): # Define a function that will make a GET request to a REST API and save the response to a JSON file.
    print ()

    json_string = json.dumps(data, indent=4) # Converts the dictionary to a JSON-formatted string with indentation. Only useful
    #for printing. Use the response.json() for getting the real dict format.
    print(json_string) 
    print(type(json_string))
    print ()

def user_auth():

    url = 'http://192.168.0.119/api/auth/login'
    
    # Define the payload with the username and password
    login_payload = {
    'username': 'admin',
    'password': 'eve',
    'html5': '-1'
    }
    response = requests.post(url, json=login_payload)

    if response.status_code == 200:
        print('Logging to ', url)
        print('Login successful')
    else:
        print('Login failed')
        pprint(response.text)
        exit()
    return response
if __name__ == "__main__": # If the script is run directly.

    response = user_auth()

    data_url = 'http://192.168.0.119/api/labs/Ansiblelab.unl/nodes/18' # Define the URL for the REST API.

    get_response = requests.get(data_url, cookies=response.cookies) # Make a GET request to the REST API.
    data = get_response.json() # Get the JSON response as a Python dictionary
    
    get_data (data)  # Serialize the data dictionary to a JSON file.