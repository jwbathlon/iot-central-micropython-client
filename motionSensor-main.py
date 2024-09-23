import machine
from machine import Pin
import time
import bluetooth

# Set up GPIO
PIR_PIN = 14
LED_PIN = "LED"

pir = Pin(PIR_PIN, Pin.IN)
led = Pin(LED_PIN, Pin.OUT)

# Initialize Bluetooth
bt = bluetooth.BLE()
bt.active(True)

def send_bluetooth_notification():
    # Advertise the device
    bt.gap_advertise(100, b'\x02\x01\x06\x03\x03\xE0\xFF\x0F\x09Motion Detected')
    print("Bluetooth notification sent")

def flash_led(times, duration):
    for _ in range(times):
        led.on()
        time.sleep(duration)
        led.off()
        time.sleep(duration)

try:
    print("PIR Module Test (CTRL+C to exit)")
    time.sleep(2)
    print("Ready")

    while True:
        if pir.value():
            print("Motion Detected!")
            flash_led(3, 0.5)
            send_bluetooth_notification()
        time.sleep(1)

except KeyboardInterrupt:
    print("Quit")