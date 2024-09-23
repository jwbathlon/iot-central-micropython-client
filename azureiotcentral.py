from utime import sleep
import cred
import utime

def log_message(message, level="INFO"):
    """Log a message to a file with a specified level."""
    with open('log_azu.txt', 'a') as log_file:
        log_file.write("{0}:{1}:{2}\n".format(utime.localtime(), level, message))

#https://github.com/Azure/iot-central-micropython-client/tree/master


try:
    import iotc
except:
    import mip
    mip.install('github:Azure/iot-central-micropython-client/package.json')
    log_message("Azure IoT Central Micropython client installed.")
    import iotc
    
from iotc import IoTCClient,IoTCConnectType,IoTCLogLevel,IoTCEvents,ConsoleLogger,IoTCLogLevel

# Initialize client with credentials
scope_id = cred.scope_id
device_id = cred.device_id
conn_type = IoTCConnectType.DEVICE_KEY # or use DEVICE_KEY if working with device keys
key = cred.key
logger = ConsoleLogger(IoTCLogLevel.ALL)
client = IoTCClient(scope_id, device_id, conn_type, key, logger)
#client.set_log_level(IoTCLogLevel.ALL)

def on_properties(name, value):
    log_message(f'Received property {name} with value {value}')
    print(f'Received property {name} with value {value}')
    return value

def on_commands(command, ack):
    log_message(f'Command {command.name}.')
    print(f'Command {command.name}.')
    ack(command, command.payload)

def on_enqueued(command):
    log_message(f'Enqueued Command {command.name}.')
    print(f'Enqueued Command {command.name}.')

def setup_callbacks():
    client.on(IoTCEvents.PROPERTIES, on_properties)
    client.on(IoTCEvents.COMMANDS, on_commands)
    client.on(IoTCEvents.ENQUEUED_COMMANDS, on_enqueued)

def main():
    setup_callbacks()
    print("Attempting to connect to Azure IoT Central...")
    log_message("Azure Attempting to connect...")

    while not client.is_connected():
        client.connect()
        if client.is_connected():
            print("Connected to Azure IoT Central")
            log_message("Connected to Azure IoT Central")
            break
        else:
            print("Connection failed, retrying...")
            log_message("Azure Connection failed, retrying...")
            utime.sleep(5)  # Wait for 5 seconds before retrying

    # Additional verification step
    if client.is_connected():
        print("Verified: Client is connected to Azure IoT Central")
        log_message("Verified: Client is connected to Azure IoT Central")
    else:
        print("Verification failed: Client is not connected")
        log_message("Verification failed: Client is not connected")

    # Debugging: Check the state of the client object
    print(f"Client object state: {client.__dict__}")

if __name__ == "__main__":
    try:
        main()
    except AttributeError as e:
        print(f"Unhandled exception: {e}")