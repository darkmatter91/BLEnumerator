# BLEnumerator

This Python script provides a menu-driven interface to interact with Bluetooth Low Energy (BLE) devices. It allows you to:

- Scan for nearby BLE devices.
- Connect to a selected device.
- Enumerate its services and characteristics.
- Read values from readable characteristics.
- Write values to writable characteristics.
- Log all interactions to a plain text file for later analysis.

The tool also attempts to guess the purpose of each characteristic based on its properties and, for readable characteristics, the value read. This can help you understand what each characteristic might be used for, especially for standard Bluetooth SIG-defined characteristics.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Main Menu](#main-menu)
  - [Device Menu](#device-menu)
- [Logging](#logging)
- [Customization](#customization)
- [License](#license)

---

## Prerequisites

To use this tool, you’ll need the following:

- **Python 3.7 or higher**: Ensure Python is installed on your system. Check your version with `python --version`.
- **BLE-capable hardware**: A Bluetooth adapter that supports BLE (most modern laptops and desktops include this).
- **Operating System**: Compatible with Windows, macOS, and Linux. On Linux, you may need elevated permissions or specific group settings (see [Installation](#installation)).

---

## Installation

Follow these steps to set up the BLE Interaction Tool:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/darkmatter91/BLEnumerator.git
   cd BLEnumerator
   ```

2. **Install dependencies**:
   The script relies on two Python libraries: `bleak` (for BLE communication) and `colorama` (for colored terminal output). Install them with:
   ```bash
   pip install bleak colorama
   ```

3. **Linux-specific setup** (if applicable):
   - On Linux, BLE access might require elevated permissions. Run the script with `sudo`:
     ```bash
     sudo python BLEnumerator.py
     ```
   - Alternatively, add your user to the `bluetooth` group to avoid using `sudo`:
     ```bash
     sudo usermod -aG bluetooth $USER
     ```
     Log out and back in for this change to take effect.

---

## Usage

### Running the Script

Start the tool by executing the Python file:
```bash
python BLEnumerator.py
```
- Ensure Bluetooth is enabled on your system before running the script.

### Main Menu

When you run the script, you’ll see the main menu with these options:

- **1. Scan for Devices**: Scans for nearby BLE devices for 10 seconds and displays a numbered list of discovered devices.
- **2. Exit**: Quits the script.

Example:
```
--- Main Menu ---
1. Scan for Devices
2. Exit
Select an option (1-2): 1
```

After selecting "Scan for Devices," you’ll see a list like this:
```
Discovered Devices:
1. S31 4F4E LE (XX:XX:XX:XX:XX:XX)
2. Unknown (XX:XX:XX:XX:XX:XX)
Select a device (1-2): 1
```
Enter the number of the device you want to connect to.

### Device Menu

Once connected to a device, a new menu appears with these options:

- **1. List Characteristics**: Shows all services and characteristics of the device, including their properties (e.g., read, write, notify) and guessed purposes.
- **2. Read from a Characteristic**: Lists readable characteristics; select one to read its value.
- **3. Write to a Characteristic**: Lists writable characteristics; select one and enter a hex value (e.g., `0x42`) to write.
- **4. Disconnect and Exit**: Disconnects from the device and returns to the main menu.

Example:
```
--- Device Menu ---
1. List Characteristics
2. Read from a Characteristic
3. Write to a Characteristic
4. Disconnect and Exit
Select an option (1-4): 2
Readable Characteristics:
1. c44f42b1-f5cf-479b-b515-9f1bb0099c99 - Properties: [read, notify]
Select a characteristic (1-1): 1
2025-03-05 13:00:15,700 - BLE_Hack - INFO - Value of c44f42b1-...-9c99: 42 (Decimal: 66) - Purpose: Vendor-specific: Possibly a sensor value or status (real-time updates)
```

---

## Logging

Every action—scanning, connecting, enumerating, reading, or writing—is logged to a file named `ble_dump_<timestamp>.txt` (e.g., `ble_dump_20250305_130000.txt`). This file includes timestamps and detailed information, making it useful for debugging or analysis.

Example log entry:
```
2025-03-05 13:00:12,601 - INFO - Services and Characteristics:
2025-03-05 13:00:12,602 - INFO - Service: 0000fe07-0000-1000-8000-00805f9b34fb - Vendor specific
2025-03-05 13:00:12,603 - INFO -   Characteristic: c44f42b1-f5cf-479b-b515-9f1bb0099c98 - Properties: [write-without-response] - Purpose: Vendor-specific: Likely a command or control input
```

---

## Customization

You can tweak the script to suit your needs:

- **Expand UUID Database**: The script uses a small set of standard Bluetooth SIG UUIDs to identify characteristics. Add more to the `STANDARD_UUIDS` dictionary in the code.
- **Enhance Purpose Guessing**: Modify the `guess_characteristic_purpose()` function to better interpret your device’s characteristics.
- **Enable Notifications**: Add support for characteristics with the `notify` property to receive real-time updates.
- **Change Log Location**: Update the `log_file` variable to save logs elsewhere.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
