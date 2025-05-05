"""
Main script for EVE-NG automation.

This script automates the deployment of multiple vendor devices in EVE-NG
using Python. It handles authentication, node creation, and configuration
through multithreading.

GitHub: https://github.com/jotape75
"""

import logging
from utils import file_path, gather_valid_creds, display_message, color_text
from processing import user_auth, run_threads, threading_process
import datetime

# Configure logging
timestamp = datetime.datetime.now()
formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
LOG_FILE = f'/home/user/pystudies/myenv/pythonbasic/projects/eve-ng_automation/log/{formatted_timestamp}_main_log_file.log'  # Specify the log file path
logging.basicConfig(
    filename=LOG_FILE,  # Log file
    level=logging.DEBUG,  # Log level (DEBUG captures all levels)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S"  # Date format
)

def main():

    """
    Main function to execute the EVE-NG automation workflow.

    This function orchestrates the entire process of automating the deployment
    of multiple vendor devices in EVE-NG. It performs the following tasks:

    1. Displays an introductory message:
        - Calls `color_text()` to retrieve color codes for styling.
        - Calls `display_message(colors)` to display an ASCII art banner and project details.

    2. Loads configuration and credentials:
        - Calls `file_path()` to load configuration files, device payloads, API URLs, and other details.

    3. Authenticates with the EVE-NG API:
        - Calls `gather_valid_creds(data["creds"])` to retrieve valid credentials.
        - Calls `user_auth(eve_API_creds, eve_ng_url_login, eve_authorization_header, colors)` 
          to authenticate with the EVE-NG API and obtain a session token.

    4. Deploys and configures devices:
        - Calls `run_threads()` to handle the creation, starting, connecting, and configuration 
          of devices in EVE-NG using multithreading.

    Args:
        None

    Returns:
        None
    """

    # Define the nodes to be created
    # Each dictionary represents a node type and the number of instances to create
    # Uncomment the nodes you want to deploy.
    # Make sure the number of nodes matches with the number of sheets in the Excel file.
 
    nodes = [
        {'Cisco Router': 4},
        {'Cisco Switch': 3},
        {'Arista Switch': 2},
        {'Juniper Firewall': 2}
    ]

    try:
        # Display the introductory message
        colors = color_text()  # Get color codes
        message = display_message(colors)
        print()
        print(message)

        # Load configuration and credentials
        (
            data,
            router_payload,
            switch_payload,
            aristasw_payload,
            juniperfw_payload,
            eve_ng_url_login,
            eve_node_creation_url,
            eve_authorization_header,
            eve_start_nodes_url,
            eve_node_port,
            eve_interface_connection,
            node_interface,
            network_mgmt,
            router_config,
            switch_config,
            aristasw_config,
            juniperfw_config,
        ) = file_path()

        # Authenticate with EVE-NG
        eve_API_creds = gather_valid_creds(data["creds"])
        response, headers = user_auth(
            eve_API_creds, 
            eve_ng_url_login, 
            eve_authorization_header, 
            colors
        )
        # Run threads for node creation and configuration
        run_threads(
            nodes,
            response,
            threading_process,
            headers,
            router_payload,
            switch_payload,
            aristasw_payload,
            juniperfw_payload,
            eve_node_creation_url,
            eve_start_nodes_url,
            eve_node_port,
            eve_interface_connection,
            node_interface,
            network_mgmt,
            router_config,
            switch_config,
            aristasw_config,
            juniperfw_config,
            colors,
        )

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()