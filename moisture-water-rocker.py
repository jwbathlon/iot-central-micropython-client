# Connect wire #1 to Pin 36/3.3V
# Connect wire #2 to Pin GP15
# Connect moisture sensor to an analog pin (e.g., GP26)
# Connect sensor V to a GPIO pin (e.g., GP14)
# Connect sensor G to GND

# Load libraries
import machine
import uasyncio as asyncio

LED = machine.Pin("LED", machine.Pin.OUT)  # Use on board LED to show switch state

# Create 'objects' for our actual Switch and Moisture Sensor
Rocker_Sw = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)
Moisture_Sensor = machine.ADC(26)  # Assuming the moisture sensor is connected to GP26 (ADC0)
Sensor_Power = machine.Pin(14, machine.Pin.OUT)  # GPIO pin to control sensor power

# Flag to indicate switch state
switch_pressed = False

def switch_handler(pin):
    global switch_pressed
    switch_pressed = pin.value()

# Attach interrupt to the switch pin
Rocker_Sw.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=switch_handler)

async def read_moisture_sensor():
    global switch_pressed
    while True:
        if switch_pressed:  # If switch is pressed
            LED.value(1)
            Sensor_Power.value(1)  # Turn on the sensor power
            await asyncio.sleep(2)  # Wait for the sensor to stabilize
            moisture_value = Moisture_Sensor.read_u16()  # Read the moisture sensor value
            print("Moisture Level:", moisture_value)
            Sensor_Power.value(0)  # Turn off the sensor power
            await asyncio.sleep(2)  # Wait for the sensor to stabilize
            # Enter light sleep for 1 minute
            for _ in range(60):  # Check the switch state every second for 1 minute
                if not switch_pressed:  # If the switch is released
                    LED.value(0)  # Turn off the LED immediately
                    break
                await asyncio.sleep(1)
        else:  # If switch is not pressed
            LED.value(0)  # Ensure LED is turned off when the switch is off
            await asyncio.sleep(0.1)  # Slow down the loop so we can see the printing

async def main():
    await read_moisture_sensor()

print("Ready, Set, GO!")
asyncio.run(main())