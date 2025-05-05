import json
import pandas as pd
from exceptions import FileNotFoundError, InvalidConfigurationError, InvalidDataError
import pyfiglet
import logging

logger = logging.getLogger()


def display_message(colors):
    """
    Display an ASCII art message with a border and additional information.
    Args:
        colors (dict): A dictionary containing color codes for formatting.
    Returns:
        str: The formatted message with ASCII art and additional information.
    """
   
     
    # Generate smaller ASCII art using the "univers" font
    ascii_art = pyfiglet.figlet_format("Hand of God", font="standard")
    ascii_lines = ascii_art.splitlines()  # Split the ASCII art into lines

    # Determine the width of the square
    max_width = max(len(line) for line in ascii_lines)  # Find the widest line in the ASCII art
    square_width = max(max_width, 50)  # Ensure the square is at least 50 characters wide

    # Create the top border of the square
    message = f"{colors.get('green')}" + "#" * (square_width + 4) + "\n"

    # Add empty padding lines
    message += f"# {''.ljust(square_width)} #\n" * 2

    # Add the ASCII art inside the square
    for line in ascii_lines:
        message += f"# {line.ljust(square_width)} #\n"

    # Add the additional message and center it
    additional_message = "Eve-ng multiple vendor automated \ndevice deployment using Python"
    for line in additional_message.split("\n"):
        message += f"# {line.center(square_width)} #\n"

    # Add more empty padding lines
    message += f"# {''.ljust(square_width)} #\n" * 2

    # Add the GitHub profile and center it
    github_line = "GitHub Profile:  https://github.com/jotape75"
    message += f"# {colors.get('yellow')}{github_line.center(square_width)}{colors.get('reset')}{colors.get('green')} #\n"

    # Add more empty padding lines
    message += f"# {colors.get('green')}{''.ljust(square_width)} #\n" * 2

    # Create the bottom border of the square
    message += "#" * (square_width + 4) + f"{colors.get('reset')}\n"

    return message

def color_text():
    """
    Define color codes for terminal output.

    Returns:
        dict: A dictionary containing color codes for formatting.   
    """

    # Define color codes for terminal output
    green = "\033[1;32m"
    red = "\033[1;31m"
    yellow = "\033[1;33m"
    blue = "\033[1;34m"
    reset = "\033[0m"
    colors = {
        "green": green,
        "red": red,
        "yellow": yellow,
        "blue": blue,
        "reset": reset
    }
    return colors

def file_path():
    """
    Load configuration files and device payloads.
    This function reads the configuration file 'automation_urls.json' and
    the Excel file containing device credentials. It also loads JSON files
    containing device payloads for different types of devices.
    Returns:
        tuple: 
        A tuple containing the loaded data, including device credentials,
        payloads, and API URLs.

        Raises:
        FileNotFoundError: If the configuration file or Excel file is not found.
        InvalidConfigurationError: If the configuration file is invalid or malformed.
        InvalidDataError: If the data in the Excel file is invalid or incomplete.
    """

    try:
        # Open the configuration file
        with open('/home/user/pystudies/myenv/pythonbasic/projects/eve-ng_automation/data/automation_urls.json', 'r') as config_file:
            files_path = json.load(config_file)

            database_file = files_path["urls"]['data_file']
            eve_ng_url_login = files_path["api_urls"]["eve_ng_url_login"]
            eve_node_creation_url = files_path['api_urls']['eve_node_creation_url']
            eve_authorization_header = files_path['eve_authorization_header']
            router_node = files_path["urls"]["router_node_url"]
            switch_node = files_path["urls"]["switch_node_payload"]
            aristasw_node = files_path["urls"]["aristasw_node_payload"]
            juniperfw_node = files_path["urls"]["juniperfw_node_payload"]
            eve_start_nodes_url = files_path["api_urls"]["eve_start_node_url"]
            eve_node_port = files_path["api_urls"]["eve_node_port"]
            eve_interface_connection = files_path["api_urls"]["eve_interface_connection_url"]
            node_interface = files_path["api_urls"]["eve_node_interface_url"]
            network_mgmt = files_path["api_urls"]["eve_network_mgmt_url"]
            router_config = files_path["urls"]["router_config"]
            switch_config = files_path["urls"]["switch_config"]
            aristasw_config = files_path["urls"]["aristasw_config"]
            juniperfw_config = files_path["urls"]["juniperfw_config"]

    except FileNotFoundError:
        logger.error("The configuration file 'automation_urls.json' was not found.")
        raise FileNotFoundError("The configuration file 'automation_urls.json' was not found.")
        
    except json.JSONDecodeError:
        logger.error("The configuration file 'automation_urls.json' is invalid or malformed.")
        raise InvalidConfigurationError("The configuration file 'automation_urls.json' is invalid or malformed.")
        

    try:
        # Open the Excel file
        db_info = pd.read_excel(
            database_file,
            sheet_name=None,
            na_values=[],
            keep_default_na=False
    )
    except FileNotFoundError:
        logger.error(f"The Excel file '{database_file}' was not found.")
        raise FileNotFoundError(f"The Excel file '{db_info}' was not found.")
    except ValueError:
        logger.error(f"The Excel file '{database_file}' is invalid or malformed.")
        raise InvalidDataError(f"The Excel file '{db_info}' is missing required sheets or data.")
    
    try:
        # Extract data from Excel sheets
        data = {
            "creds": db_info['creds'][["Device type", "Host", "Username", "Password", "Secret"]].dropna().to_dict(orient="records") 

        }
    except KeyError as e:
        logger.error(f"Missing required data in the Excel file: {e}")
        raise InvalidDataError(f"Missing required data in the Excel file: {e}")
    try:
        # Open the JSON files with devices eve_ng payload

        with open(router_node, 'r') as router_payload_file,\
         open(switch_node, 'r') as switch_payload_file, \
         open(aristasw_node, 'r') as aristasw_payload_file, \
         open(juniperfw_node, 'r') as juniperfw_payload_file:
                    
            router_payload = json.load(router_payload_file)
            switch_payload = json.load(switch_payload_file)
            aristasw_payload = json.load(aristasw_payload_file)
            juniperfw_payload = json.load(juniperfw_payload_file)
  

    except FileNotFoundError:
        logger.error(f"The file '{router_node}' was not found.")
        raise FileNotFoundError(f"The file '{router_node}' was not found.")
    
    return data, \
        router_payload, \
        switch_payload, \
        aristasw_payload,\
        juniperfw_payload,\
        eve_ng_url_login,\
        eve_node_creation_url,\
        eve_authorization_header,\
        eve_start_nodes_url,\
        eve_node_port,\
        eve_interface_connection,\
        node_interface,\
        network_mgmt,\
        router_config,\
        switch_config,\
        aristasw_config,\
        juniperfw_config


def gather_valid_creds(creds):
    """
    Read device credentials from an Excel sheet and convert them into a dictionary.

    Args:
        file_path (str): Path to the Excel file.
        sheet_name (str): Name of the sheet containing credentials.

    Returns:
        list: A list of dictionaries, each representing a device's credentials.
    """
    try:
        # Validate input
        if not isinstance(creds, list):
            logger.error("The 'creds' input must be a list of dictionaries.")
            raise ValueError("The 'creds' input must be a list of dictionaries.")

        # Initialize lists for FTD and Linux devices
        eve_API_creds = []
        eve_ssh_creds = []

        # Iterate over the credentials data
        for row in creds:
            # Validate required keys
            required_keys = ["Device type", "Host", "Username", "Password"]
            for key in required_keys:
                if key not in row:
                    logger.error(f"Missing required key '{key}' in credentials data.")
                    raise ValueError(f"Missing required key '{key}' in credentials data.")

            # Create a device dictionary
            device = {
                "device_type": row["Device type"],
                "host": row["Host"],
                "username": row["Username"],
                "password": row["Password"],
            }
            # Add the "secret" field if it exists
            if "Secret" in row and row["Secret"]:
                device["secret"] = row["Secret"]
            # Separate devices based on their type
            if row["Device type"] == "eve_ng":
                eve_API_creds.append(device)
            if row["Device type"] == "eve_ng_ssh":  
                eve_ssh_creds.append(device)    
        return eve_API_creds
    except ValueError as e:
        logger.error(f"Invalid data in the credentials: {e}")
        raise ValueError(f"Invalid data in the credentials: {e}")
    except Exception as e:
        logger.error(f"An error occurred while processing credentials: {e}")
        raise Exception(f"An error occurred while processing credentials: {e}")