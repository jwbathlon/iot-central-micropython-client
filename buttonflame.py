import machine
import utime
#wires flame sensor 26
#V to VSYS
#G to GND
#button
#S to 28
#V to 3.3V (out)
#buzzer
#S to 1
#V to 3.3V (out)

# Initialize the power control pin (GPIO 2 in this example)
power_control_pin = machine.Pin(2, machine.Pin.OUT)

# Set the power control pin to low initially to turn off the power
power_control_pin.value(0)

# Wait for 5 seconds
utime.sleep(5)

# Set the power control pin to high to turn on the power
power_control_pin.value(1)


# Initialize the LED pin (GPIO 13 in this example)

led = machine.Pin("LED", machine.Pin.OUT)
buzzer = machine.Pin(1, machine.Pin.OUT)

# Initialize the button pin (GPIO 28 in this example) with an internal pull-up resistor
button_pin_number = 28
button = machine.Pin(button_pin_number, machine.Pin.IN, machine.Pin.PULL_UP)

# Initialize the flame sensor on pin A0 (ADC pin)
flame_sensor_pin = 26  # A0 corresponds to ADC pin 26
flame_sensor = machine.ADC(flame_sensor_pin)

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

# Function to read the flame sensor
def read_flame_sensor():
    # Read the analog value (0-65535)
    analog_value = flame_sensor.read_u16()
    # Assuming a threshold value to detect flame
    threshold = 30000  # Adjust this threshold based on your sensor's output
    return analog_value < threshold

# Set up an interrupt on the button pin to call toggle_led on falling edge
button.irq(trigger=machine.Pin.IRQ_FALLING, handler=toggle_led)

# Keep the program running
while True:
    if led.value() == 1:  # LED is on
        flame_detected = read_flame_sensor()
        if flame_detected:  # Flame detected
            print("Flame detected!")
            # Blink the LED fast and sound the buzzer
            for _ in range(10):  # Blink 10 times
                led.value(not led.value())
                buzzer.value(1)  # Turn on the buzzer
                utime.sleep(0.1)  # Fast blink delay
                buzzer.value(0)  # Turn off the buzzer
        else:
            print("No flame detected.")
            utime.sleep(0.5)  # Small delay to prevent excessive CPU usage
    else:
        utime.sleep(0.1)  # Small delay to prevent excessive CPU usage