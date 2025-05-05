# **EVE-NG Automation Project**

This project automates the deployment and configuration of multiple vendor devices in **EVE-NG** using Python. It supports multithreading for efficient handling of tasks like node creation, starting, connecting, and configuration.

---

## **Features**

- **Multi-Vendor Support**: Automates deployment for Cisco, Arista, and Juniper devices.
- **Multithreading**: Speeds up the process by handling multiple tasks concurrently.
- **Dynamic Configuration**: Reads device credentials and configurations from external files.
- **Error Handling**: Includes robust exception handling for better debugging.
- **Customizable**: Easily extendable to support additional device types or configurations.

---

## **Project Structure**

```
eve-ng_automation
├── src
│   ├── main.py          # Entry point of the application
│   ├── utils.py         # Utility functions (e.g., file handling, ASCII art)
│   ├── exceptions.py    # Custom exceptions for error handling
│   └── processing.py    # Core logic for interacting with the EVE-NG API
├── data
│   ├── automation_urls.json  # Configuration file for API URLs and payloads
│   ├── router_node.json      # Payload for Cisco routers
│   ├── cicosw_node.json      # Payload for Cisco switches
│   ├── aristasw_node.json    # Payload for Arista switches
│   ├── juniperfw_node.json   # Payload for Juniper firewalls
│   ├── Switch.xlsx           # Excel file for Cisco Switch configurations
│   ├── vEOS.xlsx             # Excel file for Arista Switch configurations
│   ├── vIOS.xlsx             # Excel file for Cisco Router configurations
│   └── vSRX-NG.xlsx          # Excel file for Juniper Firewall configurations
├── requirements.txt      # Project dependencies
├── .gitignore            # Files to ignore in version control
└── README.md             # Project documentation
```

---

## **Installation**

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd eve-ng_automation
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## **Configuration**

1. **Edit the `automation_urls.json` File**:
   - Update the file with the correct API URLs, payloads, and configuration paths.

2. **Prepare the Payload Files**:
   - Ensure the following JSON files in the `data` folder are properly configured:
     - `router_node.json`: Contains the payload for Cisco routers.
     - `cicosw_node.json`: Contains the payload for Cisco switches.
     - `aristasw_node.json`: Contains the payload for Arista switches.
     - `juniperfw_node.json`: Contains the payload for Juniper firewalls.

3. **Prepare the Excel Files**:
   - Ensure the following Excel files in the `data` folder are properly configured:
     - `Switch.xlsx`: Contains configuration data for Cisco switches.
     - `vEOS.xlsx`: Contains configuration data for Arista switches.
     - `vIOS.xlsx`: Contains configuration data for Cisco routers.
     - `vSRX-NG.xlsx`: Contains configuration data for Juniper firewalls.

---

## **Usage**

To run the application, execute the following command:

```bash
python src/main.py
```

### **Workflow**

1. **Displays an ASCII Art Banner**:
   - The script starts by displaying a banner with project details.

2. **Loads Configuration and Credentials**:
   - Reads configuration files and device credentials.

3. **Authenticates with EVE-NG**:
   - Logs into the EVE-NG API using the provided credentials.

4. **Deploys and Configures Devices**:
   - Creates, starts, connects, and configures devices in EVE-NG using multithreading.

---

## **Dependencies**

The project requires the following Python libraries:

- `requests`
- `pandas`
- `pyfiglet`
- `tqdm`

Install them using:
```bash
pip install -r requirements.txt
```

---

## **Error Handling**

- **FileNotFoundError**: Raised if a required file (e.g., `automation_urls.json`) is missing.
- **InvalidConfigurationError**: Raised for invalid or malformed configuration files.
- **InvalidDataError**: Raised for missing or invalid data in the credentials file.

---

## **Logging**

- `main_logfile.log`: Captures high-level logs for monitoring application behavior.

## **Troubleshooting**

- If you find any issue on connecting to EVE api, please use the `eve_api_connection_test.py` for connectivity testing. Just change the username, password and urls for basic connectivity testing.

## **Contributing**

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

---

## **License**

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## **Maintenance and Updates**

This project is actively maintained to ensure compatibility with the latest versions of EVE-NG and Python. Here's how updates and maintenance are handled:

1. ## **Bug Fixes**:

Known issues are tracked in the GitHub Issues section.
Fixes are prioritized based on their impact and severity.

2. ## **Feature Updates**:


New features, such as support for additional vendors or device types, are added periodically.
Suggestions for new features are welcome! Feel free to open an issue or submit a pull request.

3. ## **Compatibility**:

The project is tested with the latest versions of Python and EVE-NG.
Dependencies are updated regularly to ensure compatibility and security.

4. ## **Community Contributions**:

Contributions from the community are encouraged. If you'd like to contribute, please follow the guidelines in the Contributing section.

## **Versioning**:

The project follows semantic versioning (e.g., v1.0.0).
Major updates, minor improvements, and patches are documented in the Changelog.

---

## **Contact**

For any questions or support, feel free to reach out:

- **GitHub**: [jotape75](https://github.com/jotape75)
- **Email**: [degraus@gmail.com]
- **Linkedin**: [https://www.linkedin.com/in/joaopaulocp/]