import machine
import network
import uasyncio as asyncio
import wifi4
import azureiotcentral
import weather
import cputemp

#summary of code.  list pins used and what they are connected to and a brief description of what the code does
# Connect wire #1 to Pin 36/3.3V
# Connect wire #2 to Pin GP15
# Connect moisture sensor to an analog pin (e.g., GP26)
# Connect sensor V to a GPIO pin (e.g., GP14)
# Connect sensor G to GND

interval = 7200  # Interval in seconds to take the moisture sensor reading

#async def deepleep():
#    machine.deepsleep(60000)

# Create 'objects' for our actual Switch and Moisture Sensor
Rocker_Sw = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)
Moisture_Sensor = machine.ADC(26)  # Assuming the moisture sensor is connected to GP26 (ADC0)
Sensor_Power = machine.Pin(14, machine.Pin.OUT)  # GPIO pin to control sensor power

LED = machine.Pin("LED", machine.Pin.OUT)  # Use on board LED to show switch state
wlan = network.WLAN(network.STA_IF)  # Define the 'wlan' variable

# Initialize switch_pressed with the current state of the switch
switch_pressed = Rocker_Sw.value()

# Flag to track if "Switch is not pressed" message has been printed
switch_not_pressed_message_shown = False

def switch_handler(pin):
    global switch_pressed
    switch_pressed = pin.value()

# Attach interrupt to the switch pin
Rocker_Sw.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=switch_handler)

# read_rocker_switch logic
async def read_switch():
    global switch_pressed, switch_not_pressed_message_shown
    while not switch_pressed:  # Wait until the switch is pressed
        if not switch_not_pressed_message_shown:
            print("Switch is off")
            switch_not_pressed_message_shown = True  # Set the flag to indicate the message has been shown
        await asyncio.sleep(1)
    print("Switch is on")
switch_not_pressed_message_shown = False  # Reset the flag

# azure iot central
async def azureiotcentraldata():
    while True:
        Sensor_Power.value(1)  # Turn on the sensor power
        await asyncio.sleep(3)  # Wait for the sensor to stabilize
        moisture_value = Moisture_Sensor.read_u16()  # Read the moisture sensor value
        print("Moisture Level:", moisture_value)
        Sensor_Power.value(0)
        
        try:
            # Get the current temperature in Wolfeboro, NH
            station_id, temperature, unit, humidity = weather.get_current_temperature_and_humidity()
            humidity = float(humidity.replace('%', '')) if isinstance(humidity, str) else humidity  # remove the % sign and convert to float
        except (ValueError, TypeError):
            temperature = -99
            unit = "N/A"
            humidity = -99

        print(f"Current temperature {station_id}  {temperature} {unit} Humidity: {humidity}")  

        cpu_temp = cputemp.get_cpu_temperature()
        print(f"CPU temperature: {cpu_temp} C")
        
    # Check if connected before sending data
        if not hasattr(azureiotcentral, 'client') or azureiotcentral.client is None:
            print("Azure IoT Central client is not initialized.")
            await asyncio.sleep(5)  # Skip this iteration if client is not initialized
            return  # Return to main loop
    
    # Connect to Azure IoT Central
        azureiotcentral.client.connect()
        if azureiotcentral.client.is_connected():
            azureiotcentral.client.send_telemetry({
            'ConnectedSSID': wifi4.wlan.config('essid'),
            'SoilMoisture': moisture_value,
            'WeatherStationID': station_id,
            'OutdoorTemperature': temperature,
            'OutdoorHumidity': humidity,
            'CPUTemperature': cpu_temp
        })
        
            print("Data sent to Azure IoT Central.")
            await asyncio.sleep(5)
            break
        else:
            print("Data not sent to Azure IoT Central.")
            await asyncio.sleep(5)
            break
            #machine.reset()  # Reset the device

# Main function to continuously read the moisture sensor
async def main():
    while True:
        #await deepleep()  #WARNING REMOVE WHEN TESTING
        await read_switch()
        await asyncio.sleep(3)  # Wait before retrying
        await wifi4.connect_wifi(LED)
        await azureiotcentraldata()
        await wifi4.wifi_cleanup(wlan, LED)
        print(f"gonna sleep for {interval} seconds")
        await asyncio.sleep(interval)  # Add a small delay to prevent a tight loop


print("Ready, Set, GO!")
# asyncio.run(main())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        Sensor_Power.value(0)  # Ensure the sensor power is turned off
        print("Program interrupted by user")
    except Exception as e:
        Sensor_Power.value(0)  # Ensure the sensor power is turned off
        print(f"Unhandled exception in main: {e}")
        print("Resetting device...")
        machine.reset()  # Reset the device
    finally:
    # Clean up resources, if necessary
        Sensor_Power.value(0)  # Ensure the sensor power is turned off
        asyncio.run(wifi4.wifi_cleanup(wlan, LED))
        print("Program terminated")