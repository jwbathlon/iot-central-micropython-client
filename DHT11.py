import machine
from machine import Pin
import wifi2
from dht import DHT11
import utime
from utime import sleep
import azureiotcentral
import gc # garbage collector
import weather
import cputemp

utime.sleep(1)

def log_message(message, level="INFO"):
    """Log a message to a file with a specified level."""
    with open('log_main.txt', 'a') as log_file:
        log_file.write("{0}:{1}:{2}\n".format(utime.localtime(), level, message))

interval = 60 * 60 # first number is minutes

led = machine.Pin('LED', machine.Pin.OUT)
dataPin = 16
myPin = Pin(dataPin, Pin.OUT,Pin.PULL_DOWN)
sensor=DHT11(myPin)

# blink the LED 3 times slowly
for i in range(3):
    led.value(1)
    utime.sleep(1)
    led.value(0)
    utime.sleep(1)

def get_next_collection_time():
    print("Collecting data...")
    sensor.measure()
    temp = sensor.temperature() * 9/5.0 + 32
    hum = sensor.humidity()
    print("Indoor Temperature: ", temp, "F")
    print("Indoor Humidity: ", hum, "%")

    # Get the current temperature in Wolfeboro, NH
    temperature, unit, humidity = weather.get_current_temperature_and_humidity()
    humidity = float(humidity.replace('%', '')) if isinstance(humidity, str) else humidity # remove the % sign and convert to float
    print(f"Current temperature KLCI: {temperature} {unit} Humidity: {humidity}")

    # Get the CPU temperature
    cpu_temp = cputemp.get_cpu_temperature()
    print(f"CPU temperature: {cpu_temp} C")

    # Check if connected before sending data
    if azureiotcentral.client.is_connected():
        azureiotcentral.client.send_telemetry({'IndoorTemperature': temp, 'IndoorHumidity': hum, 'OutdoorTemperature': temperature, 'OutdoorHumidity': humidity, 'CPUTemperature': cpu_temp})
        # blink the LED fast to indicate data was sent
        for i in range(3):
            led.value(1)
            utime.sleep(0.5)
            led.value(0)
            utime.sleep(0.5)
        print("Data sent to Azure IoT Central.")
    else:
        # try to reconnect
        azureiotcentral.client.connect()
        azureiotcentral.client.send_telemetry({'IndoorTemperature': temp, 'IndoorHumidity': hum, 'OutdoorTemperature': temperature, 'OutdoorHumidity': humidity, 'CPUTemperature': cpu_temp})
        print("Not connected to Azure IoT Central. reconnected and sent.")

    #print the device_id from the azureiotcentral.py file
    print("Device ID: ", azureiotcentral.device_id)

def main():
    # Initialize variables or flags if necessary
    while True:
        try:
            wifi2.connect_to_wifi()
            log_message("Connected to WiFi")
            sleep(2)  # Give some time for the connection to establish
            
            # Check if the azureiotcentral.client is properly initialized
            if not hasattr(azureiotcentral, 'client') or azureiotcentral.client is None:
                print("Azure IoT Central client is not initialized.")
                log_message("Azure IoT Central client is not initialized.")
                # Initialization code for azureiotcentral.client should go here
                continue  # Skip this iteration if client is not initialized

            # Connect to Azure IoT Central
            azureiotcentral.client.connect()
            get_next_collection_time()
            log_message("Get next collection time.")
            wifi2.wifi_cleanup()
            gc.collect()
            sleep(interval)
        except AttributeError as e:
            print(f"Encountered an error: {e}")
            log_message(f"Encountered an error: {e}")
            # Handle the error or re-initialize resources as needed
            # Consider a delay or a mechanism to prevent immediate retry in case of persistent errors
            sleep(10)  # Delay before retrying to prevent immediate failure loop

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"Unhandled exception: {e}")
    finally:
        # Clean up resources, if necessary
        wifi2.wifi_cleanup()
        print("Program terminated")
