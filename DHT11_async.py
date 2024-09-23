import network
import machine
from machine import Pin
import uasyncio as asyncio
from dht import DHT11
import azureiotcentral
import weather
import cputemp
import wifi4
import gc # garbage collector

interval = 30 * 60  # first number is minutes

LED = machine.Pin('LED', machine.Pin.OUT)
wlan = network.WLAN(network.STA_IF)  # Define the 'wlan' variable
dataPin = 16
myPin = Pin(dataPin, Pin.OUT, Pin.PULL_DOWN)
sensor = DHT11(myPin)

#return the name of the network the device is connected to
#def get_network_name():
#    wlan = network.WLAN(network.STA_IF)
#    return wlan.config('essid')

async def blink_led(times, delay):
    for _ in range(times):
        LED.value(1)
        await asyncio.sleep(delay)
        LED.value(0)
        await asyncio.sleep(delay)

async def get_next_collection_time():
    while True:
        await wifi4.connect_wifi(LED)
        print("Collecting data...")
        sensor.measure()
        temp = sensor.temperature() * 9/5.0 + 32
        hum = sensor.humidity()
        print("Indoor Temperature: ", temp, "F")
        print("Indoor Humidity: ", hum, "%")

        try:
            # Get the current temperature in Wolfeboro, NH
            station_id, temperature, unit, humidity = weather.get_current_temperature_and_humidity()
            humidity = float(humidity.replace('%', '')) if isinstance(humidity, str) else humidity  # remove the % sign and convert to float
        except (ValueError, TypeError):
            temperature = -99
            unit = "N/A"
            humidity = -99


        print(f"Current temperature {station_id} {temperature} {unit} Humidity: {humidity}")

        # Get the CPU temperature
        cpu_temp = cputemp.get_cpu_temperature()
        print(f"CPU temperature: {cpu_temp} C")

                # Check if connected before sending data
#        if not hasattr(azureiotcentral, 'client') or azureiotcentral.client is None:
#            print("Azure IoT Central client is not initialized.")
#            # Initialization code for azureiotcentral.client should go here
#            await asyncio.sleep(interval)  # Skip this iteration if client is not initialized
#            continue

        # Connect to Azure IoT Central
    # Connect to Azure IoT Central
        azureiotcentral.client.connect()
        if azureiotcentral.client.is_connected():
            azureiotcentral.client.send_telemetry({
            'ConnectedSSID': wifi4.wlan.config('essid'),
            'IndoorTemperature': temp,
            'IndoorHumidity': hum,
            'WeatherStationID': station_id,
            'OutdoorTemperature': temperature,
            'OutdoorHumidity': humidity,
            'CPUTemperature': cpu_temp
            })
            # blink the LED fast to indicate data was sent
            await blink_led(3, 0.5)
            print("Data sent to Azure IoT Central.")
        else:
            print("Not connected to Azure IoT Central.")
            #try to reconnect after 10 seconds
            await asyncio.sleep(10)
            continue

#wait 5 seconds before disconnecting from WiFi
        await asyncio.sleep(5)
        # Disconnect from WiFi
        await wifi4.wifi_cleanup(wlan, LED)
        gc.collect()
        await asyncio.sleep(interval)

async def main():
    await blink_led(3, 1)
    await get_next_collection_time()

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
        asyncio.run(wifi4.wifi_cleanup(wlan, LED))
        print("Program terminated")