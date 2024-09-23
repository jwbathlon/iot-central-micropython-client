from machine import Pin, time_pulse_us, PWM
from utime import sleep
import time
#cables
#Motor Yellow GPIO 4
#Motor Red Vbus
#Motor brown GND
#
#echo sensor
#vcc vbus
#echo GPIO 3
#trigger GPIO 2
#Grey GND
#

# Define pins
TRIGGER_PIN = 2
ECHO_PIN = 3
SERVO_PIN = 4

# Set up pins
trigger = Pin(TRIGGER_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
led = Pin("LED", Pin.OUT)
servo = PWM(Pin(SERVO_PIN), freq=50)  # Servo control using PWM

def get_distance():
    # Send a 10us pulse.
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)

    # Wait for the pulse to come back. The pulse
    # goes from low to high so we measure a positive pulse.
    duration = time_pulse_us(echo, 1)
    distance = duration * 0.0343 / 2

    return distance

def setServoCycle(position):
    servo.duty_u16(position)
    sleep(0.01)


def calculate_duty_cycle(angle):
    # Calculate the duration of the high level pulse (5% to 25% of the period)
    duration_percentage = 5 + (angle / 180.0) * (25 - 5)
    # Convert the duration to a duty cycle between 0 and 65535
    duty_cycle = int(duration_percentage / 100.0 * 65535)
    return duty_cycle

DUTY_0 = calculate_duty_cycle(0)
DUTY_180 = calculate_duty_cycle(180)



# Modify the main loop
while True:
    distance = get_distance()
    distance_feet = int(distance * 0.0328084)  # Convert cm to feet
    distance_inches = (distance * 0.393701) % 12  # Convert the remainder to inches
    print("Distance is: %d feet %.1f inches" % (distance_feet, distance_inches))

    if distance <= 30.48:  # 1 foot is 30.48 cm
        led.on()
        for pos in range(DUTY_0, DUTY_180, 50):
            setServoCycle(pos)
        for pos in range(DUTY_180, DUTY_0, -50):
            setServoCycle(pos)
    else:
        led.off()
        sleep(2)
