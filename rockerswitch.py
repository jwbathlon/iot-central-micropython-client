# Connect wire #1 to Pin 36/3.3V
# Connect wire #2 to Pin GP15
# Connect buzzer S to Pin GP16
# Connect buzzer V to Pin 36/3.3V
# Connect buzzer G to GND

# Load libraries
import machine
import utime

LED = machine.Pin("LED", machine.Pin.OUT)  # Use on board LED to show switch state

# Create 'objects' for our actual Switch and Buzzer
Rocker_Sw = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_DOWN)
Buzzer = machine.Pin(16, machine.Pin.OUT)

# Polling method using compare to handle an ON-OFF switch
print("Ready, Set, GO!")
while True:  # Run an endless loop
    if Rocker_Sw.value() == True:  # If input GP15 is HIGH
        LED.value(1)
        Buzzer.value(1)
        print("ON")
    elif Rocker_Sw.value() == False:  # If input GP15 is LOW
        LED.value(0)
        Buzzer.value(0)
        print("OFF")

    utime.sleep(0.1)  # Slow down the loop so we can see the printing