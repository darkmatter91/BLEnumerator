#!/usr/bin/env python3
# BLEnumerator.py - A tool for interacting with Bluetooth Low Energy (BLE) devices

import asyncio
from bleak import BleakScanner, BleakClient
import logging
from colorama import init, Fore, Style
from datetime import datetime
import colorama

# Initialize colorama for colored output
colorama.init(autoreset=True)

# Configure colored logging for console
class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.INFO: Fore.GREEN + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + Style.RESET_ALL,
        logging.ERROR: Fore.RED + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + Style.RESET_ALL,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Set up logging
logger = logging.getLogger("BLEnumerator")
logger.setLevel(logging.INFO)

# Console handler with colored output
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())
logger.addHandler(console_handler)

# File handler for plain text dump
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"ble_dump_{timestamp}.txt"
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

# Standard UUID database (subset for example)
STANDARD_UUIDS = {
    "00002a00-0000-1000-8000-00805f9b34fb": "Device Name (readable string)",
    "00002a01-0000-1000-8000-00805f9b34fb": "Appearance (device category)",
    "00002a05-0000-1000-8000-00805f9b34fb": "Service Changed (indicates service updates)",
    "00002a29-0000-1000-8000-00805f9b34fb": "Manufacturer Name String",
}

def guess_characteristic_purpose(char, value=None):
    """Guess the purpose of a characteristic based on UUID, properties, and value."""
    uuid = char.uuid
    props = char.properties
    
    # Check if it's a standard UUID
    if uuid in STANDARD_UUIDS:
        return STANDARD_UUIDS[uuid]
    
    # Vendor-specific UUID: make educated guesses
    guess = "Vendor-specific: "
    if "read" in props and "notify" in props:
        guess += "Possibly a sensor value or status (real-time updates)"
    elif "read" in props:
        guess += "Possibly a status, configuration, or static data"
    elif "write" in props or "write-without-response" in props:
        guess += "Likely a command or control input"
    elif "notify" in props:
        guess += "Possibly a notification-only status or event"
    else:
        guess += "Unknown purpose"

    # Add value-based hints if available
    if value:
        try:
            dec_value = int.from_bytes(value, "little")
            hex_value = value.hex()
            if 0 <= dec_value <= 100:
                guess += f" (Value: {hex_value}/{dec_value} - could be percentage, temp, etc.)"
            elif dec_value in [0, 1]:
                guess += f" (Value: {hex_value}/{dec_value} - possibly on/off or boolean)"
            else:
                guess += f" (Value: {hex_value}/{dec_value} - possibly a counter or raw data)"
        except:
            guess += f" (Value: {value.hex()} - format unknown)"
    
    return guess

async def scan_for_devices():
    """Scan for nearby BLE devices and return a list."""
    logger.info("Scanning for BLE devices (10 seconds)...")
    devices = await BleakScanner.discover(timeout=10.0)
    if not devices:
        logger.warning("No devices found.")
        return []
    for device in devices:
        logger.info(f"Discovered: {device.address} - {device.name or 'Unnamed Device'}")
    return devices

async def enumerate_device(client):
    """Enumerate services and characteristics of a connected device."""
    services = await client.get_services()
    char_list = []
    
    logger.info("Services and Characteristics:")
    for service in services:
        logger.info(f"Service: {service.uuid} - {service.description}")
        for char in service.characteristics:
            props = ", ".join(char.properties)
            purpose = guess_characteristic_purpose(char)
            logger.info(f"  Characteristic: {char.uuid} - Properties: [{props}] - Purpose: {purpose}")
            char_list.append(char)
    return char_list

async def read_characteristic(client, char):
    """Read the value of a specific characteristic."""
    try:
        value = await client.read_gatt_char(char.uuid)
        purpose = guess_characteristic_purpose(char, value)
        logger.info(f"Value of {char.uuid}: {value.hex()} (Decimal: {int.from_bytes(value, 'little')}) - Purpose: {purpose}")
    except Exception as e:
        logger.error(f"Failed to read {char.uuid}: {e}")

async def write_characteristic(client, char):
    """Write a value to a specific characteristic."""
    try:
        value = input("Enter hex value to write (e.g., '010203'): ").strip()
        data = bytes.fromhex(value)
        await client.write_gatt_char(char.uuid, data)
        logger.info(f"Wrote {value} to {char.uuid}")
    except ValueError:
        logger.error("Invalid hex string. Use format like '010203'.")
    except Exception as e:
        logger.error(f"Failed to write to {char.uuid}: {e}")

async def connect_and_interact(device):
    """Connect to a device and provide a menu for interaction."""
    address = device.address
    name = device.name or "Unnamed Device"
    
    logger.info(f"Connecting to {name} ({address})...")
    try:
        async with BleakClient(address) as client:
            if not await client.is_connected():
                logger.error(f"Failed to connect to {name} ({address})")
                return
            
            logger.info(f"Connected to {name} ({address})")
            characteristics = await enumerate_device(client)
            readable_chars = [c for c in characteristics if "read" in c.properties]
            writable_chars = [c for c in characteristics if "write" in c.properties or "write-without-response" in c.properties]

            while True:
                print("\n--- Device Menu ---")
                print("1. List Characteristics")
                print("2. Read from a Characteristic")
                print("3. Write to a Characteristic")
                print("4. Disconnect and Exit")
                choice = input("Select an option (1-4): ").strip()

                if choice == "1":
                    await enumerate_device(client)
                elif choice == "2":
                    if not readable_chars:
                        logger.warning("No readable characteristics available.")
                        continue
                    
                    print("\nReadable Characteristics:")
                    for i, char in enumerate(readable_chars, 1):
                        print(f"{i}. {char.uuid} - Properties: [{', '.join(char.properties)}]")
                    
                    try:
                        char_idx = int(input("Select a characteristic (1-{}): ".format(len(readable_chars)))) - 1
                        if 0 <= char_idx < len(readable_chars):
                            await read_characteristic(client, readable_chars[char_idx])
                        else:
                            logger.error("Invalid selection.")
                    except ValueError:
                        logger.error("Please enter a valid number.")
                elif choice == "3":
                    if not writable_chars:
                        logger.warning("No writable characteristics available.")
                        continue
                    
                    print("\nWritable Characteristics:")
                    for i, char in enumerate(writable_chars, 1):
                        print(f"{i}. {char.uuid} - Properties: [{', '.join(char.properties)}]")
                    
                    try:
                        char_idx = int(input("Select a characteristic (1-{}): ".format(len(writable_chars)))) - 1
                        if 0 <= char_idx < len(writable_chars):
                            await write_characteristic(client, writable_chars[char_idx])
                        else:
                            logger.error("Invalid selection.")
                    except ValueError:
                        logger.error("Please enter a valid number.")
                elif choice == "4":
                    logger.info("Disconnecting...")
                    break
                else:
                    logger.error("Invalid option. Choose 1-4.")

    except Exception as e:
        logger.error(f"Error with {name} ({address}): {e}")

async def main():
    """Main function with menu-driven BLE interaction."""
    # Banner
    print("\033[1mBLEnumerator\033[0m")
    print("\033[91mAuthor: Darkmatter91 (https://github.com/darkmatter91)\033[0m")
    print()  # Adds a blank line for separation

    logger.info(f"Starting BLEnumerator. Log file: {log_file}")
    
    while True:
        print("\n--- Main Menu ---")
        print("1. Scan for Devices")
        print("2. Exit")
        choice = input("Select an option (1-2): ").strip()

        if choice == "1":
            devices = await scan_for_devices()
            if not devices:
                continue

            print("\nDiscovered Devices:")
            for i, device in enumerate(devices, 1):
                name = device.name or "Unnamed Device"
                print(f"{i}. {name} ({device.address})")
            
            try:
                dev_idx = int(input("Select a device (1-{}): ".format(len(devices)))) - 1
                if 0 <= dev_idx < len(devices):
                    await connect_and_interact(devices[dev_idx])
                else:
                    logger.error("Invalid selection.")
            except ValueError:
                logger.error("Please enter a valid number.")
        elif choice == "2":
            logger.info("Exiting...")
            break
        else:
            logger.error("Invalid option. Choose 1-2.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script terminated by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
