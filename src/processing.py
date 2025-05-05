import requests 
import datetime 
import uuid 
from telnetlib import Telnet
import time
import datetime
import pandas as pd
import threading
from queue import Queue
from tqdm import tqdm
import logging

logger = logging.getLogger()

# This function will be called to authenticate with the EVE-NG API
def user_auth(eve_API_creds,eve_ng_url_login,eve_authorization_header,colors):
    """
    Authenticate with the EVE-NG API using the provided credentials.
    Args:
        eve_API_creds (list): List of dictionaries containing EVE-NG API credentials.
        eve_ng_url_login (str): URL for EVE-NG login.
        eve_authorization_header (str): Authorization header for EVE-NG API.
        colors (dict): Dictionary containing color codes for terminal output.
    Returns:
        tuple: A tuple containing the response object and headers for further API calls.
    """
    # Extract username and password from the credentials

    username = eve_API_creds[0]['username']
    password = eve_API_creds[0]['password']

    headers = {
        'Authorization': eve_authorization_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Define the payload with the username and password
    login_payload = {
        'username': username,
        'password': password,
        'html5': '-1'
    }
    response = requests.post(eve_ng_url_login, json=login_payload, headers=headers)

    if response.status_code == 200:
        print(f'\n{colors.get("green")}logger to EVE-ng API - {eve_ng_url_login}{colors.get("reset")}')
        print(f'{datetime.datetime.now()} - Login successful\n')
        logger.info('logger to EVE-ng API - {eve_ng_url_login}')
    else:
        print(f'\n{datetime.datetime.now()} - Login failed')
        print(response.text)
        logger.info(f'\n{datetime.datetime.now()} - Login failed')
        exit()
    return response,headers

# This function will be called to create nodes in EVE-NG
def create_nodes(dev_num, node_type, device_payload, *args):
    (
        response,
        headers,
        eve_node_creation_url,
        eve_start_nodes_url,
        eve_node_port,
        eve_interface_connection,
        node_interface,
        network_mgmt,
        createnode_queue,
        starnode_queue,
        connectnode_queue,
        configure_queue,
        closeconnection_queue,
        lock,
        colors
    ) = args

    """
    Create nodes in EVE-NG using the provided payload.
    Args:
        dev_num (int): Device number for the node.
        node_type (str): Type of the node (e.g., Router, Switch).
        device_payload (dict): Payload containing node configuration.
        args (tuple): Additional arguments for API calls.
    Returns:
        str: The ID of the created node.
    """

    max_retries = 3  # Number of retries for node creation
    for attempt in range(max_retries):
        try:
            # Assign a unique UUID to the device payload
            logger.info(f"Attempting to create node {node_type} (Attempt {attempt + 1}/{max_retries}).")
            device_payload['uuid'] = str(uuid.uuid4())
            if dev_num == 1:
                device_payload['top'] = "30"  # Example adjustment for specific devices

            # Send the API request to create the node
            create_node_api = requests.post(eve_node_creation_url, json=device_payload, headers=headers, cookies=response.cookies)
            logger.debug(f"Create Node API Response: {create_node_api.text}")

            # Check if the node creation was successful
            if create_node_api.status_code != 201:
                raise ValueError(f"Failed to create node: {create_node_api.text}")

            # Parse the response to get the device ID
            create_node_response = create_node_api.json()
            device_id = create_node_response['data']['id']
            logger.info(f"Node {node_type} with ID {device_id} created successfully.")
            createnode_queue.put(f'{datetime.datetime.now()} - {node_type} - Eve-ng Node {device_id} created successfully')

            # Get device interface
            node_interface_api = requests.get(node_interface.format(device_id=device_id), headers=headers, cookies=response.cookies)
            node_interface_response = node_interface_api.json()
            node_interface_id = node_interface_response["data"]["ethernet"][0]["name"]
            logger.info(f"Node {node_type} with ID {device_id} has interface {node_interface_id}.")

            # Get management network name
            mgmt_net_api = requests.get(network_mgmt, headers=headers, cookies=response.cookies)
            mgmt_net_response = mgmt_net_api.json()
            mgmt_net_id = mgmt_net_response['data']['name']
            logger.info(f"Management network ID for {node_type} with ID {device_id}: {mgmt_net_id}.")

            # Connect device to management network
            interfaces = '{"0":"21"}'  # Adjust the management network ID for your environment
            interface_connection_api = requests.put(eve_interface_connection.format(device_id=device_id), data=interfaces, headers=headers, cookies=response.cookies)
            logger.info(f"Connected {node_type} with ID {device_id} to management network.")

            # Log success for interface connection
            createnode_queue.put(f'{datetime.datetime.now()} - Connecting MGMT interface {node_interface_id} of {node_type} Eve-ng id {device_id} to management network {mgmt_net_id}')

            return device_id

        except Exception as e:
            # Log the error and retry if attempts remain
            logger.error(f"Attempt {attempt + 1} to create node failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait before retrying
            else:
                # If all retries fail, log and raise the error
                createnode_queue.put(f'{datetime.datetime.now()} - Node creation failed after {max_retries} attempts')
                logger.critical(f"Failed to create node {node_type} after {max_retries} attempts.")
                raise

    # This part should never be reached due to the raise statement above
    return None
# This function will be called to start nodes in EVE-NG
def start_nodes(device_id, node_type, *args):
    (
        response,
        headers,
        eve_node_creation_url,
        eve_start_nodes_url,
        eve_node_port,
        eve_interface_connection,
        node_interface,
        network_mgmt,
        createnode_queue,
        starnode_queue,
        connectnode_queue,
        configure_queue,
        closeconnection_queue,
        lock,
        colors
    ) = args

    logger.info(f"Attempting to start node {node_type} with ID {device_id}.")
    starnode_queue.put(f'{datetime.datetime.now()} - Starting {node_type} Eve-ng node {device_id} ')

    # Send the API request to start the node
    start_node_api = requests.get(eve_start_nodes_url.format(device_id=device_id), headers=headers, cookies=response.cookies)
    time.sleep(3)  # Add a delay of 3 seconds

    if start_node_api.status_code == 200:
        logger.info(f"Node {node_type} with ID {device_id} started successfully.")
        starnode_queue.put(f'{datetime.datetime.now()} - Node {device_id} - {node_type} started successfully')

        # Poll the EVE-NG API to check if the node is running
        max_retries = 10  # Maximum number of retries
        retry_delay = 5  # Delay between retries in seconds
        for attempt in range(max_retries):
            node_status_api = requests.get(f"{eve_node_creation_url}/{device_id}", headers=headers, cookies=response.cookies)
            if node_status_api.status_code == 200:
                try:
                    node_status = node_status_api.json().get('data', {}).get('status', None)
                    logger.debug(f"Node {node_type} with ID {device_id} status: {node_status} (Attempt {attempt + 1}/{max_retries})")
                    
                    if node_status == 2:  # 2 indicates the node is running
                        logger.info(f"Node {node_type} with ID {device_id} is running.")
                        return True  # Exit the function as the node is ready
                    elif node_status == 0:  # 0 indicates the node is stopped
                        logger.warning(f"Node {node_type} with ID {device_id} is stopped. (Attempt {attempt + 1}/{max_retries})")
                        start_node_api = requests.get(eve_start_nodes_url.format(device_id=device_id), headers=headers, cookies=response.cookies)
                        if start_node_api.status_code == 200:
                            logger.info(f"Retry to start node {node_type} with ID {device_id} was successful.")
                        else:
                            logger.error(f"Retry to start node {node_type} with ID {device_id} failed. Response: {start_node_api.text}")
                    else:
                        logger.warning(f"Unexpected status for node {node_type} with ID {device_id}: {node_status}")
                except Exception as e:
                    logger.error(f"Error parsing node status for {node_type} with ID {device_id}: {e}")
            else:
                logger.error(f"Failed to retrieve status for node {node_type} with ID {device_id}. Response: {node_status_api.text}")
            time.sleep(retry_delay)  # Wait before checking again

        # If the node is not ready after retries
        logger.error(f"Node {node_type} with ID {device_id} failed to start in time.")
        starnode_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - Node {device_id} - {node_type} failed to start in time{colors.get("reset")}')
    else:
        logger.error(f"Failed to start node {node_type} with ID {device_id}. Response: {start_node_api.text}")
        starnode_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - Failed to start Eve-ng {device_id} - {node_type}{colors.get("reset")}')

    return False

def get_node_port(device_id,*args):
    (
        response,
        headers,
        eve_node_creation_url,
        eve_start_nodes_url,
        eve_node_port,
        eve_interface_connection,
        node_interface,
        network_mgmt,
        createnode_queue,
        starnode_queue,
        connectnode_queue,
        configure_queue,
        closeconnection_queue,
        lock,
        colors
    ) = args

    """
    Get the port information for the created node.
    Args:
        device_id (str): The ID of the device to get port information for.
        args (tuple): Additional arguments for API calls.
    Returns:
        tuple: A tuple containing the port number and name.
    """

    # Get node port information
    node_port_api = requests.get(eve_node_port.format(device_id=device_id), headers=headers, cookies=response.cookies)
    port = node_port_api.json()['data']['url'].split(':')[-1]
    name = node_port_api.json()['data']['name']
    return port, name

# This function will be called to configure the node using Telnet
# Eve-ng uses Telnet to connect to the nodes as a console connection

def telnet_conn(port,name,device_id,dev_num,node_type,dev_config_file,*args):
    (
        response,
        headers,
        eve_node_creation_url,
        eve_start_nodes_url,
        eve_node_port,
        eve_interface_connection,
        node_interface,
        network_mgmt,
        createnode_queue,
        starnode_queue,
        connectnode_queue,
        configure_queue,
        closeconnection_queue,
        lock,
        colors
    ) = args

    """
    Connect to the node using Telnet and apply the initial configuration.
    Args:
        port (str): The port number for the Telnet connection.
        name (str): The name of the node.
        device_id (str): The ID of the device.
        dev_num (int): The device number.
        node_type (str): Type of the node (e.g., Router, Switch).
        dev_config_file (str): Path to the configuration file.
        args (tuple): Additional arguments for API calls.
    Returns:
        None
    """
    # Telnet connection
    # Define the Telnet connection parameters
    TELNET_TIMEOUT = 10
    HOST = '192.168.0.119'
    tn = None  # Initialize tn to None to avoid issues for non-Telnet devices
    def dev_config(dev_config_file, tn, device_id, node_type):
        try:
            # Load the configuration file
            commands_config = pd.read_excel(dev_config_file, sheet_name=None)
            logger.info(f"Available sheets in configuration file: {list(commands_config.keys())}")
            
            # Check if the sheet for the current device exists
            if str(dev_num) in commands_config:
                commands = commands_config[str(dev_num)]['Command'].dropna().tolist()
                logger.info(f"Applying configuration for {node_type} (Device ID: {device_id}, Dev Num: {dev_num}).")
                configure_queue.put(f"{datetime.datetime.now()} - Applying configuration to {node_type} (Device ID: {device_id}, Dev Num: {dev_num}).")
                # Send each command via Telnet
                for command in commands:
                    logger.info(f"Sending command to {node_type} (Device ID: {device_id}): {command}")
                    tn.write(f"{command}\n".encode('ascii'))
                    output = tn.read_until(b"#", timeout=10).decode('ascii', errors='ignore')
                    logger.debug(f"Response for command '{command}' on {node_type} (Device ID: {device_id}): {output}")
            else:
                logger.warning(f"No configuration found for {node_type} (Device ID: {device_id}, Dev Num: {dev_num}). Skipping configuration.")
                configure_queue.put(f"{datetime.datetime.now()} - No configuration found for {node_type} (Device ID: {device_id}, Dev Num: {dev_num}). Skipping configuration.")
        except Exception as e:
            logger.error(f"Error applying configuration to {node_type} (Device ID: {device_id}): {e}")
            configure_queue.put(f"{colors.get('red')}{datetime.datetime.now()} - Error applying configuration to {node_type} (Device ID: {device_id}): {e}{colors.get('reset')}")

    try:
        if name == 'vIOS':
            # Create a Telnet object and connect to the server
            logger.info(f"Connecting to {node_type} (Device ID: {device_id}) on port {port} via Telnet.")

            tn = Telnet(HOST, port)
            connectnode_queue.put(f"{datetime.datetime.now()} - Connected to the {node_type} - node {device_id} on port {port}")
            while True:
                output = tn.read_until(b"[yes/no]:", timeout=TELNET_TIMEOUT)
                if b"[yes/no]:" in output:
                    tn.write(b"no\r\n")
                    break
            time.sleep(2)  # Add a small delay to give the device time to process the input                  
            # Wait for the "Press RETURN to get started!" prompt
            tn.read_until(b"Press RETURN to get started!", timeout=TELNET_TIMEOUT)
            logger.debug(f"Telnet connection established for {node_type} (Device ID: {device_id}).")

            # Send a newline character to proceed
            tn.write(b"\r\n")
            while True:
                output = tn.read_very_eager().decode('ascii')
                #print(output)  # Print the output for debugging purposes
                if "(Config Wizard)" in output:
                    tn.write(b"\r\n")
                    time.sleep(2)  # Add a small delay to give the device time to process the input
                    break
                time.sleep(1)  # Wait for a short period before checking again
            # Wait for the enable prompt
            tn.read_until(b"Router>", timeout=TELNET_TIMEOUT)
            logger.debug(f"Telnet prompt for {node_type} (Device ID: {device_id}): {output}")
            # Send "enable" command
            tn.write(b"enable\n")
            # Wait for the enable prompt
            tn.read_until(b"#", timeout=TELNET_TIMEOUT)
            # Send "terminal length 0" command to avoid pagination
            logger.debug(f"Telnet enable prompt for {node_type} (Device ID: {device_id}): {output}")

            tn.write(b"terminal length 0\n")
            time.sleep(2)  # Add a 2-second delay
            output = tn.read_very_eager().decode('ascii', errors='ignore')
            logger.debug(f"Telnet terminal length 0 prompt for {node_type} (Device ID: {device_id}): {output}")
            # Wait for the prompt
            tn.read_very_eager()  # Clear the buffer
            tn.read_until(b"#", timeout=TELNET_TIMEOUT)
            logger.info(f"Applying configuration to {node_type} (Device ID: {device_id}).")
            dev_config(dev_config_file, tn, device_id, node_type)
            

        elif name == 'Switch':
            tn = Telnet(HOST, port)
            connectnode_queue.put(f"{datetime.datetime.now()} - Connected to the {node_type} - node {device_id} on port {port}")
            logger.info(f"Connecting to {node_type} (Device ID: {device_id}) on port {port} via Telnet.")
            tn.read_until(b"signing verification", timeout=TELNET_TIMEOUT)
            tn.write(b"\r\n")
            tn.read_until(b"Switch>", timeout=TELNET_TIMEOUT)
            # Send "enable" command
            tn.write(b"enable\n")
            tn.read_until(b"#", timeout=TELNET_TIMEOUT)
            # Send "terminal length 0" command to avoid pagination
            tn.write(b"terminal length 0\n")
            # Wait for the prompt
            tn.read_until(b"#", timeout=TELNET_TIMEOUT)
            dev_config(dev_config_file, tn, device_id, node_type)
        elif name == 'vEOS':
            #### Arista Switch
            tn = Telnet(HOST, port)
            connectnode_queue.put(f"{datetime.datetime.now()} - Connected to the {node_type} - node {device_id} on port {port}")
            logger.info(f"Connecting to {node_type} (Device ID: {device_id}) on port {port} via Telnet.")
            while True:
                output = tn.read_very_eager().decode('ascii')
                #print(output)  # Print the output for debugging purposes
                if "localhost login:" in output:
                    tn.write(b"admin\n")
                    time.sleep(2)  # Add a small delay to give the device time to process the input
                    break
                time.sleep(1)  # Wait for a short period before checking again
            tn.read_until(b"localhost>", timeout=TELNET_TIMEOUT)
            # Close the connection
            tn.write(b"enable\n")
            tn.read_until(b"#", timeout=TELNET_TIMEOUT)
            tn.write(b"zerotouch cancel\n")
            connectnode_queue.put(f"{datetime.datetime.now()} - {node_type} node {device_id} is rebooting, please wait for a few minutes")	
            logger.info(f"Rebooting {node_type} (Device ID: {device_id}).")
            while True:
                output = tn.read_very_eager().decode('ascii')
                #print(output)  # Print the output for debugging purposes
                if "localhost login:" in output:
                    tn.write(b"admin\n")
                    time.sleep(2)  # Add a small delay to give the device time to process the input
                    break
                time.sleep(1)  # Wait for a short period before checking again
            tn.read_until(b"localhost>", timeout=TELNET_TIMEOUT)
            tn.write(b"enable\n")
            tn.read_until(b"#", timeout=TELNET_TIMEOUT)
            dev_config(dev_config_file, tn, device_id, node_type)
        elif name == 'vSRX-NG':
            tn = Telnet(HOST, port)
            connectnode_queue.put(f"{datetime.datetime.now()} - Connected to the {node_type} - node {device_id} on port {port}")
            logger.info(f"Connecting to {node_type} (Device ID: {device_id}) on port {port} via Telnet.")
            while True:
                output = tn.read_very_eager().decode('ascii')
                #print(output)  # Print the output for debugging purposes
                if "login:" in output:
                    tn.write(b"root\n")
                    time.sleep(2)  # Add a small delay to give the device time to process the input
                    break
                time.sleep(1)  # Wait for a short period before checking again
            tn.read_until(b"root@:~ #", timeout=TELNET_TIMEOUT)
            tn.write(b"cli\n")
            tn.read_until(b">", timeout=TELNET_TIMEOUT)
            time.sleep(5)  # Wait for 5 seconds before starting configuration
            logger.info(f"Applying configuration to {node_type} (Device ID: {device_id}).")
            dev_config(dev_config_file, tn, device_id, node_type)
    except Exception as e:
        configure_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - An error occurred while configuring {node_type} - node {device_id}: {e}{colors.get("reset")}')
        logger.error(f"Error during Telnet connection for {node_type} (Device ID: {device_id}): {e}")

    finally:
        # Close Telnet connection if it was initialized
        if tn:
            try:
                tn.close()
                closeconnection_queue.put(f"{datetime.datetime.now()} - Telnet connection closed for {node_type} - node {device_id}")
                logger.info(f"Telnet connection closed for {node_type} (Device ID: {device_id}).")
            except Exception as close_error:
                closeconnection_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - Error while closing Telnet connection: {close_error}{colors.get("reset")}')

# Trheading function to create and manage nodes
# This function will create threads for each node type and manage their execution
# It will also handle the termination event to ensure graceful shutdown

def run_threads(
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
    colors
):
    """
    Run threads for node creation and configuration.
    Args:
        nodes (list): List of dictionaries containing node types and their counts.
        response (requests.Response): Response object from the EVE-NG API.
        threading_process (function): Function to be executed by each thread.
        headers (dict): Headers for API requests.
        router_payload (dict): Payload for router nodes.
        switch_payload (dict): Payload for switch nodes.
        aristasw_payload (dict): Payload for Arista switch nodes.
        juniperfw_payload (dict): Payload for Juniper firewall nodes.
        eve_node_creation_url (str): URL for node creation API.
        eve_start_nodes_url (str): URL for starting nodes API.
        eve_node_port (str): URL for getting node port information.
        eve_interface_connection (str): URL for connecting interfaces API.
        node_interface (str): URL for getting node interface information.
        network_mgmt (str): URL for management network API.
        router_config (str): Path to router configuration file.
        switch_config (str): Path to switch configuration file.
        aristasw_config (str): Path to Arista switch configuration file.
        juniperfw_config (str): Path to Juniper firewall configuration file.
        colors (dict): Dictionary containing color codes for terminal output.
    """
    # Initialize queues and locks for thread-safe communication
    threads = []
    createnode_queue = Queue()
    starnode_queue = Queue()
    connectnode_queue = Queue()
    configure_queue = Queue()
    closeconnection_queue = Queue()
    lock = threading.Lock()

    # Calculate the total number of devices
    total_devices = sum(value for dev in nodes for value in dev.values())
    print(f'{colors.get("green")}Total devices to be created: {colors.get("reset")}{total_devices}\n')
    # Create a tuple of arguments to be passed to the threading_process function
    args_var = (
        response,
        headers,
        eve_node_creation_url,
        eve_start_nodes_url,
        eve_node_port,
        eve_interface_connection,
        node_interface,
        network_mgmt,
        createnode_queue,
        starnode_queue,
        connectnode_queue,
        configure_queue,
        closeconnection_queue,
        lock,
        colors
    )

    # Create progress bars with consecutive positions
    create_progress = tqdm(total=total_devices, desc=f'{colors.get("green")}Creating Nodes{colors.get("reset")}', position=0, leave=True, ncols=100)
    start_progress = tqdm(total=total_devices, desc=f'{colors.get("green")}Starting Nodes{colors.get("reset")}', position=1, leave=True, ncols=100)
    connect_progress = tqdm(total=total_devices, desc=f'{colors.get("green")}Connecting Nodes{colors.get("reset")}', position=2, leave=True, ncols=100)
    configure_progress = tqdm(total=total_devices, desc=f'{colors.get("green")}Configuring Nodes{colors.get("reset")}', position=3, leave=True, ncols=100)
    close_progress = tqdm(total=total_devices, desc=f'{colors.get("green")}Closing Connections{colors.get("reset")}', position=4, leave=True, ncols=100)
    # Create threads for all devices
    for dev in nodes:  # Loop through each dictionary in the nodes list
        for node_type, value in dev.items():  # Loop through each device type and count
            for dev_num in range(value):  # Create a thread for each instance
                if node_type == "Cisco Router":
                    th = threading.Thread(
                        target=threading_process,
                        args=(dev_num, node_type, router_payload, router_config, create_progress, start_progress, connect_progress, configure_progress, close_progress, *args_var),
                    )
                    threads.append(th)
                    time.sleep(3)  # Add a delay of 3 seconds
                elif node_type == "Cisco Switch":
                    th = threading.Thread(
                        target=threading_process,
                        args=(dev_num, node_type, switch_payload, switch_config, create_progress, start_progress, connect_progress, configure_progress, close_progress, *args_var),
                    )
                    threads.append(th)
                elif node_type == "Arista Switch":
                    th = threading.Thread(
                        target=threading_process,
                        args=(dev_num, node_type, aristasw_payload, aristasw_config, create_progress, start_progress, connect_progress, configure_progress, close_progress, *args_var),
                    )
                    threads.append(th)
                elif node_type == "Juniper Firewall":
                    th = threading.Thread(
                        target=threading_process,
                        args=(dev_num, node_type, juniperfw_payload, juniperfw_config, create_progress, start_progress, connect_progress, configure_progress, close_progress, *args_var),
                    )
                    threads.append(th)
                else:
                    print(f'{colors.get("red")}{datetime.datetime.now()} - Unsupported node type: {node_type}{colors.get("reset")}')

    # Start all threads
    for th in threads:
        th.start()

    # Wait for all threads to finish
    for th in threads:
        th.join()

    # Close progress bars
    create_progress.close()
    start_progress.close()
    connect_progress.close()
    configure_progress.close()
    close_progress.close()

    # Add a separator
    print(f'\n{colors.get("blue")}' + '-' * 50 + f'{colors.get("reset")}')
    print(f'{colors.get("green")}Task Results:{colors.get("reset")}')
    print(f'{colors.get("blue")}' + '-' * 50 + f'{colors.get("reset")}')

    # Print the output from the queues in order
    print(f'\n{colors.get("green")}#### NODE CREATION MESSAGE ####{colors.get("reset")}')
    while not createnode_queue.empty():
        print(createnode_queue.get())

    print(f'\n{colors.get("green")}#### NODE START MESSAGE ####{colors.get("reset")}')
    while not starnode_queue.empty():
        print(starnode_queue.get())

    print(f'\n{colors.get("green")}#### NODE CONNECTION MESSAGE ####{colors.get("reset")}')
    while not connectnode_queue.empty():
        print(connectnode_queue.get())

    print(f'\n{colors.get("green")}#### NODE CONFIGURATION MESSAGE ####{colors.get("reset")}')
    while not configure_queue.empty():
        print(configure_queue.get())

    print(f'\n{colors.get("green")}#### NODE CLOSURE MESSAGE ####{colors.get("reset")}')
    while not closeconnection_queue.empty():
        print(closeconnection_queue.get())

# This function will be called by each thread to handle the node creation and management
# It will call the process_node function to handle the node creation, starting, and port retrieval

def threading_process(dev_num, node_type, device_payload, dev_config_file, create_progress, start_progress, connect_progress, configure_progress, close_progress, *args):
    """
    Process a single node by creating, starting, and configuring it.
    Args:
        dev_num (int): Device number for the node.
        node_type (str): Type of the node (e.g., Router, Switch).
        device_payload (dict): Payload containing node configuration.
        dev_config_file (str): Path to the configuration file.
        create_progress (tqdm): Progress bar for node creation.
        start_progress (tqdm): Progress bar for starting nodes.
        connect_progress (tqdm): Progress bar for connecting nodes.
        configure_progress (tqdm): Progress bar for configuring nodes.
        close_progress (tqdm): Progress bar for closing connections.
        args (tuple): Additional arguments for API calls.
    Returns:    
        None
    """
    # Unpack the arguments
    (
        response,
        headers,
        eve_node_creation_url,
        eve_start_nodes_url,
        eve_node_port,
        eve_interface_connection,
        node_interface,
        network_mgmt,
        createnode_queue,
        starnode_queue,
        connectnode_queue,
        configure_queue,
        closeconnection_queue,
        lock,
        colors
    ) = args

    try:
        # Step 1: Create the node
        device_id = create_nodes(dev_num, node_type, device_payload, *args)
        create_progress.update(1)

        # Step 2: Start the node
        start_nodes(device_id, node_type, *args)
        start_progress.update(1)

        # Step 3: Get the node's port information
        port, name = get_node_port(device_id, *args)
        connect_progress.update(1)

        # Step 4: Configure the node
        telnet_conn(port, name, device_id, dev_num, node_type, dev_config_file, *args)
        configure_progress.update(1)

        # Step 5: Close the connection
        close_progress.update(1)

    except Exception as e:
        closeconnection_queue.put(f'{colors.get("red")}Error processing node {node_type} instance {dev_num}: {e}{colors.get("reset")}')