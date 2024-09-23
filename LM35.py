import machine
from machine import Pin, ADC
import utime as time
import azureiotcentral
import wifi

led = machine.Pin('LED', machine.Pin.OUT)

wifi.disconnect()

# ADC configuration for LM35 on Raspberry Pi Pico
# Assuming the LM35 is connected to GPIO 26 (ADC0)
adc = ADC(26) #GPIO 26 (ADC0)

def read_temperature():
    # Read the analog value (0-65535) and convert it to voltage
    voltage = adc.read_u16() * 3.3 / 65535
    # Convert voltage to temperature in Celsius (10mV per degree)
    temperature_c = voltage / 0.01
    return temperature_c

def countdown(duration):
    for remaining in range(duration, 0, -1):
        mins, secs = divmod(remaining, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print("\rCountdown: " + timer, end="")
        time.sleep(1)
    print("\rCountdown completed!          ")

while True:
    temp_c = read_temperature()
    temp_f = temp_c * 9/5.0 + 32  # Convert to Fahrenheit
    print("Indoor Temperature: ", temp_f, "F")
    wifi.check_and_blink()
    # Send telemetry data to Azure IoT Central using azureiotcentral.py
    #azureiotcentral.client.send_telemetry({'IndoorTemperature': temp_f})

    # Blink led after sending telemetry data
    led.value(1)
    time.sleep(1)
    led.value(0)
    time.sleep(5)
    # Replace the time.sleep(15 * 60) in your main loop with:
    # countdown(15 * 60)  # 15 minutes countdown