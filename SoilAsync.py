import network
import machine
from machine import Pin, ADC
import uasyncio as asyncio
#from dht import DHT11
import azureiotcentral
import weather
import cputemp
import wifi3

import gc # garbage collector

# Define the 3V3_EN pin
#en_pin = Pin(3, Pin.OUT)

# Function to disable power to the AD0 pin
#def disable_power():
#    en_pin.value(0)  # Pull the 3V3_EN pin LOW to disable power

# Call the function to disable power
#disable_power()


# Define the GPIO pin that controls the power to the sensor ADC(0)
#POWER_CONTROL_PIN = 26

# Initialize the power control pin
#power_control = machine.Pin(POWER_CONTROL_PIN, machine.Pin.OUT)

# DEEP SLEEP COMMENT OUT IF TESTING
#interval = 20 * 60 
deep_sleep_interval = 30  # 30 minutes

# Charging delay in seconds
#charging_delay = 300  # 5 minutes

led = machine.Pin('LED', machine.Pin.OUT)

adc = machine.ADC(0)


#return the name of the network the device is connected to
def get_network_name():
    wlan = network.WLAN(network.STA_IF)
    return wlan.config('essid')

async def blink_led(times, delay):
    for _ in range(times):
        led.value(1)
        await asyncio.sleep(delay)
        led.value(0)
        await asyncio.sleep(delay)

# Put the device into deep sleep
async def go_to_deep_sleep():
    while True:
        print("Going to deep sleep for {} minute.".format(deep_sleep_interval))
       # power_control.value(0)  # Disable power to the sensor
        await asyncio.sleep(0)  # Yield control to the event loop
        machine.deepsleep(deep_sleep_interval * 60000)


async def get_next_collection_time():
    while True:
        await asyncio.sleep(5)
        await wifi3.connect_wifi()
        print("Collecting data...")

        # Ensure moisture_value is an integer
        while True:
            try:
                moisture_value = int(adc.read_u16())
                break
            except ValueError:
                print("Moisture value is not an integer, retrying...")
                await asyncio.sleep(2)
                continue

        print("Soil Moisture: ", moisture_value)

        try:
            # Get the current temperature in Wolfeboro, NH
            station_id, temperature, unit, humidity= weather.get_current_temperature_and_humidity()
            humidity = float(humidity.replace('%', '')) if isinstance(humidity, str) else humidity  # remove the % sign and convert to float
        except (ValueError, TypeError):
            temperature = -99
            unit = "N/A"
            humidity = -99

        print(f"Current temperature {station_id}  {temperature} {unit} Humidity: {humidity}")    

        # Get the CPU temperature
        cpu_temp = cputemp.get_cpu_temperature()
        print(f"CPU temperature: {cpu_temp} C")

        # Check if connected before sending data
        if not hasattr(azureiotcentral, 'client') or azureiotcentral.client is None:
            print("Azure IoT Central client is not initialized.")
           # Initialization code for azureiotcentral.client should go here
            await asyncio.sleep(10)  # Skip this iteration if client is not initialized
            continue

        # Connect to Azure IoT Central
        azureiotcentral.client.connect()
        if azureiotcentral.client.is_connected():
            azureiotcentral.client.send_telemetry({
                'ConnectedSSID': get_network_name(),
                'SoilMoisture': moisture_value,
                'WeatherStationID': station_id,
                'OutdoorTemperature': temperature,
                'OutdoorHumidity': humidity,
                'CPUTemperature': cpu_temp
            })
            # blink the LED fast to indicate data was sent
            await blink_led(3, 0.5)
            print("Data sent to Azure IoT Central.")
            await blink_led(5, 0.2)      
            await asyncio.sleep(2) #wait 2 seconds before disconnecting from WiFi
            await wifi3.wifi_cleanup() # Disconnect from WiFi 
            await asyncio.sleep(1)

            # DEEP SLEEP COMMENT OUT IF TESTING
            #disable_power()
            await asyncio.sleep(2)
            await go_to_deep_sleep() # how long is this in deep sleep? 2 minutes
            #await asyncio.sleep(interval)
        else:
            print("Not connected to Azure IoT Central.")
            #try to reconnect after 5 seconds
            await asyncio.sleep(5)
            continue

async def main():
    # Initial charging delay
    #await asyncio.sleep(charging_delay)
    #await asyncio.sleep(1)
    #power_control.value(0)  # Enable power to the sensor
    await asyncio.sleep(1)
    #power_control.value(1)  # Enable power to the sensor
    await blink_led(3, 1)
    await get_next_collection_time()

    #gc.collect()

#    await blink_led(5, 0.2)       
    # DEEP SLEEP COMMENT OUT IF TESTING
#    go_to_deep_sleep(interval) # how long is this in deep sleep? 2 minutes

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"Unhandled exception in main: {e}")
        print("Resetting device...")
        machine.reset()  # Reset the device
    finally:
    # Clean up resources, if necessary
        asyncio.run(wifi3.wifi_cleanup())
        print("Program terminated")