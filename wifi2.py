import network
import secrets  # Ensure this file has ssid and password variables
import machine
import time
import cred
import utime


def log_message(message, level="INFO"):
    """Log a message to a file with a specified level."""
    with open('log_wifi2.txt', 'a') as log_file:
        log_file.write("{0}:{1}:{2}\n".format(utime.localtime(), level, message))

# Initialize onboard LED and WiFi
led = machine.Pin("LED", machine.Pin.OUT)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
hostname = network.hostname(cred.device_id)

def blink_led(frequency, duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        led.toggle()
        time.sleep(1 / frequency)


def connect_to_wifi(max_attempts=10):
    global connected_ssid
    print("Scanning for available WiFi networks...")
    log_message("scanning for available WiFi networks")
    available_networks = wlan.scan()
    available_ssids = [net[0].decode('utf-8') for net in available_networks]
    # Create a dictionary from secrets.WIFI_CREDENTIALS for faster lookup
    credentials_dict = {net["SSID"]: net["PASSWORD"] for net in secrets.WIFI_CREDENTIALS}

        # Check if there are any known networks in range
    known_networks_in_range = set(available_ssids) & set(credentials_dict.keys())
    if not known_networks_in_range:
        print("No known networks in range. Waiting 10 minutes before resetting the device...")
        log_message("No known networks in range. Waiting 10 minutes before resetting the device...")
        utime.sleep(600)  # Wait for 600 seconds (10 minutes)
        print("Resetting the device...")
        machine.reset()
    

    for ssid in available_ssids:
        if ssid in credentials_dict:
            print(f"Found {ssid}, trying to connect...")
            wlan.connect(ssid, credentials_dict[ssid])
            attempt = 0
            while not wlan.isconnected() and attempt < max_attempts:
                blink_led(0.5, 2)  # Blink slowly for 2 seconds
                attempt += 1
                print(f"Attempt {attempt} to connect to {ssid}")
                log_message("Attempt {attempt} to connect to {ssid}")
            if wlan.isconnected():
                blink_led(5, 2)  # Blink fast for 2 seconds
                led.on()  # Turn LED on solidly
                print("Connected to", ssid)
                log_message("Connected to {ssid}")
                print("IP Address:", wlan.ifconfig()[0])
                connected_ssid = ssid
                return True
            else:
                print(f"Failed to connect to {ssid} after {max_attempts} attempts.")
                print("Waiting 10 minutes before resetting the device...")
                utime.sleep(600)  # Wait for 600 seconds (10 minutes)
                print("Resetting the device...")
                log_message("Failed to connect to {ssid} after {max_attempts} attempts. Resetting the device...")
                machine.reset()
    print("Failed to connect to any configured network. Please check your credentials.")
    return False


#if program is stopped turn off the LED and disconnect from WiFi
def wifi_cleanup():
    global connected_ssid
    led.off()
    wlan.disconnect()
    wlan.active(False)
    log_message("Disconnected from {connected_ssid}")
    print("Disconnected from", connected_ssid)

def main():
    # Your main code here
    connect_to_wifi()
    
if __name__ == "__main__":
    main()