import machine
from machine import Pin
import time
import azureiotcentral
import wifi3
import uasyncio as asyncio

# Initialize LED
led = machine.Pin('LED', machine.Pin.OUT)

# Initialize PIR sensor
pir_sensor = Pin(17, Pin.IN)

# Flag to indicate motion detection
motion_detected = False

def pir_handler(pin):
    global motion_detected
    motion_detected = True

# Setup PIR sensor interrupt
pir_sensor.irq(trigger=Pin.IRQ_RISING, handler=pir_handler)

async def main_loop():
    global motion_detected
    while True:
        if motion_detected:
            print("Motion detected!")
            await wifi3.connect_wifi()
            # Send telemetry data to Azure IoT Central using azureiotcentral.py
            azureiotcentral.client.send_telemetry({'MotionDetected': True})
            print("telemetry sent.")
            led.value(1)
            await asyncio.sleep(1)
            led.value(0)
            motion_detected = False
        await asyncio.sleep(0.1)  # Small delay to prevent constant CPU usage

if __name__ == "__main__":
    asyncio.run(main_loop())