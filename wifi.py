import network
import secrets
import time
import machine
import socket

# Initialize global variables
led = machine.Pin('LED', machine.Pin.OUT)
wlan = network.WLAN(network.STA_IF)

def initialize_wifi():
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(secrets.SSID, secrets.PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
        print("Connected to WiFi")
        print('Network config:', wlan.ifconfig())

def blink_led(times=5, on_time=0.1, off_time=0.1):
    for _ in range(times):
        led.value(1)  # Turn LED on
        time.sleep(on_time)
        led.value(0)  # Turn LED off
        time.sleep(off_time)

def connect_and_blink():
    initialize_wifi()
    blink_led()

def check_and_blink():
    if not wlan.isconnected():
        print("WiFi not connected, connecting...")
        connect_and_blink()
    else:
        print("WiFi already connected")
        if is_internet_connected():
            print("Internet connection verified")
        else:
            print("No internet access, resetting...")
            blink_led(times=5, on_time=0.2, off_time=0.2)
            time.sleep(10)  # Short delay before reset
            machine.reset()  # Reset the device

def is_internet_connected(host="8.8.8.8", port=53, timeout=3):
    try:
        sock = socket.socket()
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return True
    except OSError:
        return False