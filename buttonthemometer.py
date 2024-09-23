import machine
import utime
#wire LM35
#S to 27
#V to 3.3V (out)
#button
#S to 28
#V to 3.3V (out)

# Initialize the onboard LED using the 'LED' identifier
led = machine.Pin("LED", machine.Pin.OUT)

# Turn on the LED initially
led.value(1)

# Initialize the button pin (GPIO 28 in this example) with an internal pull-up resistor
button_pin_number = 28
button = machine.Pin(button_pin_number, machine.Pin.IN, machine.Pin.PULL_UP)

# Initialize the LM35 temperature sensor on pin 27
temp_sensor_pin = 27
temp_sensor = machine.ADC(temp_sensor_pin)

# Debounce time in milliseconds
debounce_time = 200
last_press_time = 0

# Function to toggle the LED state
def toggle_led(pin):
    global last_press_time
    current_time = utime.ticks_ms()
    
    if pin.value() == 0:  # Button is pressed
        if utime.ticks_diff(current_time, last_press_time) > debounce_time:
            led.value(not led.value())
            last_press_time = current_time

# Function to read temperature from LM35 and convert to Fahrenheit
def read_temperature():
    # Read the analog value (0-1023)
    analog_value = temp_sensor.read_u16()
    # Convert the analog value to voltage (assuming 3.3V reference)
    voltage = analog_value * 3.3 / 65535
    # Convert the voltage to Celsius (LM35 outputs 10mV per degree Celsius)
    temp_celsius = voltage * 100
    # Convert Celsius to Fahrenheit
    temp_fahrenheit = temp_celsius * 9 / 5 + 32
    return temp_fahrenheit

# Set up an interrupt on the button pin to call toggle_led on falling edge
button.irq(trigger=machine.Pin.IRQ_FALLING, handler=toggle_led)

# Keep the program running
while True:
    if led.value() == 1:  # LED is on
        temperature = read_temperature()
        print("Temperature: {:.2f} F".format(temperature))
        utime.sleep(5)  # Wait for 5 seconds before taking the next reading
    else:
        utime.sleep(0.1)  # Small delay to prevent excessive CPU usage