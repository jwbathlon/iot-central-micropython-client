import machine
import network
import uasyncio as asyncio
import wifi4

#summary of code.  list pins used and what they are connected to and a brief description of what the code does
# Connect wire #1 to Pin 36/3.3V
# Connect wire #2 to Pin GP15
# Connect moisture sensor to an analog pin (e.g., GP26)
# Connect sensor V to a GPIO pin (e.g., GP14)
# Connect sensor G to GND



interval = 120  # Interval in seconds to take the moisture sensor reading

# Create 'objects' for our actual Switch and Moisture Sensor
Rocker_Sw = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)
Moisture_Sensor = machine.ADC(26)  # Assuming the moisture sensor is connected to GP26 (ADC0)
Sensor_Power = machine.Pin(14, machine.Pin.OUT)  # GPIO pin to control sensor power

LED = machine.Pin("LED", machine.Pin.OUT)  # Use on board LED to show switch state
LED.value(0)
wlan = network.WLAN(network.STA_IF)

# Initialize switch_pressed with the current state of the switch
switch_pressed = Rocker_Sw.value()

# Flag to track if "Switch is not pressed" message has been printed
switch_not_pressed_message_shown = False

def switch_handler(pin):
    global switch_pressed
    switch_pressed = pin.value()

# Attach interrupt to the switch pin
Rocker_Sw.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=switch_handler)

async def read_moisture_sensor():
    global switch_pressed, moisture_value, switch_not_pressed_message_shown
    if switch_pressed:  # Check if switch is pressed
        await wifi4.connect_wifi(LED)
        Sensor_Power.value(1)  # Turn on the sensor power
        await asyncio.sleep(2)  # Wait for the sensor to stabilize
        moisture_value = Moisture_Sensor.read_u16()  # Read the moisture sensor value
        print("Moisture Level:", moisture_value)
        await asyncio.sleep(2)  # Wait for the sensor to stabilize
        Sensor_Power.value(0)  # Turn off the sensor power
        await wifi4.wifi_cleanup(wlan, LED)
        print("WiFi disconnected A")
        switch_not_pressed_message_shown = False  # Reset the flag
        # Wait for 120 seconds before taking the next measurement
        print("Waiting for 120 seconds before taking the next measurement...")
        for _ in range(interval):
            if not switch_pressed:  # If the switch is released
                break
            await asyncio.sleep(1)
    else:  # If switch is not pressed
        if not switch_not_pressed_message_shown:
            print("Switch is not pressed")
            Sensor_Power.value(0)  # Turn off the sensor power
            await wifi4.wifi_cleanup(wlan, LED)
            print("WiFi disconnected B")
            switch_not_pressed_message_shown = True  # Set the flag to indicate the message has been shown
        await asyncio.sleep(.1)  # Slow down the loop so we can see the printing

# Main function to continuously read the moisture sensor
async def main():
    while True:
        await read_moisture_sensor()
        await asyncio.sleep(0.1)  # Add a small delay to prevent a tight loop

print("Ready, Set, GO!")
# asyncio.run(main())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Unhandled exception in main: {e}")
        print("Resetting device...")
       # machine.reset()  # Reset the device
    finally:
    # Clean up resources, if necessary
        Sensor_Power.value(0)
        asyncio.run(wifi4.wifi_cleanup(wlan, LED))
        print("Program terminatedx")

