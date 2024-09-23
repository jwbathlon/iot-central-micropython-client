import machine
from machine import Pin
import utime as time
import azureiotcentral 
import wifi
from dht import DHT11
import time
import ntptime
from time import sleep

led = machine.Pin('LED', machine.Pin.OUT)

dataPin = 16

myPin = Pin(dataPin, Pin.OUT,Pin.PULL_DOWN)
sensor=DHT11(myPin)

# Interval for sensor readings in minutes
SENSOR_READING_INTERVAL_MINUTES = 10
# Minute number to start the sensor readings (set to 0 for the top of the hour)
SENSOR_READING_START_MINUTE = 0

def get_next_collection_time():
    now = time.localtime()
    current_hour, current_minute, current_second = now[3], now[4], now[5]
    
    # Convert current time to total seconds since midnight
    total_current_seconds = (current_hour * 3600) + (current_minute * 60) + current_second
    
    # Calculate the total seconds for the next scheduled collection time
    # Find how many intervals have passed since midnight
    intervals_since_midnight = total_current_seconds // (SENSOR_READING_INTERVAL_MINUTES * 60)
    # Calculate next interval start time in seconds since midnight
    next_interval_seconds = (intervals_since_midnight + 1) * SENSOR_READING_INTERVAL_MINUTES * 60
    
    # If we're exactly on a scheduled time, wait for the next interval
    if total_current_seconds % (SENSOR_READING_INTERVAL_MINUTES * 60) == 0:
        return SENSOR_READING_INTERVAL_MINUTES * 60
    
    # Calculate seconds until next collection
    seconds_until_next_collection = next_interval_seconds - total_current_seconds
    
    return seconds_until_next_collection

UTC_OFFSET = -4 * 60 * 60  # Adjust as necessary

def update_time_from_ntp():
    try:
        wifi.check_and_blink_until_internet()
        ntptime.settime()
        current_time = time.time() + UTC_OFFSET
        print("Time updated from NTP server:", time.localtime(current_time))
        return time.time()  # Return the current timestamp after updating
    except Exception as e:
        print("Failed to update time from NTP server:", e)
        return None

# Initial time update and store the timestamp
last_ntp_update = update_time_from_ntp()

# Wait for the next collection time initially
next_collection_delay = get_next_collection_time()
time.sleep(next_collection_delay)

while True:
    current_time = time.time()
    
    # Calculate hours since last NTP update
    if last_ntp_update is not None:
        hours_since_last_update = (current_time - last_ntp_update) / 3600
    else:
        hours_since_last_update = 0
    
    # Calculate and print hours until next update
    hours_until_next_update = 24 - hours_since_last_update
    print(f"Next NTP update in {hours_until_next_update:.2f} hours")
    
    # Check if 24 hours have passed since the last NTP update
    if last_ntp_update is not None and (current_time - last_ntp_update) >= 86400: # 86400 seconds in a day
        last_ntp_update = update_time_from_ntp()  # Update the time and store the new update timestamp
    
    # Perform data collection
    print("Collecting data...")
    sensor.measure()
    temp = sensor.temperature() * 9/5.0 + 32
    hum = sensor.humidity()
    print("Indoor Temperature: ", temp, "F")
    print("Indoor Humidity: ", hum, "%")
    wifi.check_and_blink_until_internet()
    led.value(1)
    time.sleep(1)
    led.value(0)

    # Check if connected before sending data
    if azureiotcentral.client.is_connected():
        azureiotcentral.client.send_telemetry({'IndoorTemperature': temp, 'IndoorHumidity': hum})
        print("Data sent to Azure IoT Central.")
    else:
        # try to reconnect
        azureiotcentral.client.connect()
        azureiotcentral.client.send_telemetry({'IndoorTemperature': temp, 'IndoorHumidity': hum})
        print("Not connected to Azure IoT Central. reconnected and sent.")

    #print the device_id from the azureiotcentral.py file
    print("Device ID: ", azureiotcentral.device_id)

    # Calculate the delay until the next collection time and wait
    next_collection_delay = get_next_collection_time()
    time.sleep(next_collection_delay)