import sys
from utime import sleep
from random import randint
from machine import ADC

# If your device needs wifi before running uncomment and adapt the code below as necessary
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("ORCHARD","orchard#11")
while not wlan.isconnected():
    pass
print(wlan.isconnected())

try:
    import iotc
except:
    import mip
    mip.install('github:Azure/iot-central-micropython-client/package.json')
    import iotc
    
from iotc import IoTCClient,IoTCConnectType,IoTCLogLevel,IoTCEvents

scope_id='0ne00CDB7A3'
device_id='motion3dot'
key='v1U185Dye5PTv4OcpK+vxWXtsozict/5zDvyjphVprU='
conn_type=IoTCConnectType.DEVICE_KEY

client=IoTCClient(scope_id,device_id,conn_type,key)
client.set_log_level(IoTCLogLevel.ALL)

def on_properties(name, value):
    print('Received property {} with value {}'.format(name, value))
    return value


def on_commands(command, ack):
    print('Command {}.'.format(command.name))
    ack(command, command.payload)

def on_enqueued(command):
    print('Enqueued Command {}.'.format(command.name))


client.on(IoTCEvents.PROPERTIES, on_properties)
client.on(IoTCEvents.COMMANDS, on_commands)
client.connect()

client.send_property({'readOnlyProp':40})

#while client.is_connected():
#    client.listen()
#    print('Sending telemetry')
#    client.send_telemetry({'temperature':randint(0,20),'pressure':randint(0,20)})
#    sleep(2)

# Create an ADC object
adc = ADC(4) # Channel 4 is used for the built-in temperature sensor

# Function to read temperature
def read_temperature():
    # Read the ADC and convert it to voltage
    voltage = adc.read_u16() * 3.3 / 65535

    # Convert the voltage to temperature using the formula provided in the datasheet
    temperature_celsius = 27 - (voltage - 0.706) / 0.001721

    # Convert the temperature to Fahrenheit
    temperature_fahrenheit = temperature_celsius * 9/5 + 32

    return temperature_fahrenheit


while client.is_connected():
    client.listen()
    telemetry_data = {'temperature':read_temperature(),'pressure':randint(0,20)}
    print('Sending telemetry:', telemetry_data)
    client.send_telemetry(telemetry_data)
    sleep(2)


