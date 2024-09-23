import machine
import asyncio
import network
import socket
from secrets import WIFI_CREDENTIALS

# Define wlan at the module level
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

async def flash_led_slow(led):
    """Flash the LED slowly."""
    while True:
        led.on()
        await asyncio.sleep(1)
        led.off()
        await asyncio.sleep(1)

async def flash_led_fast(led, times):
    """Flash the LED quickly a specified number of times."""
    for _ in range(times):
        led.on()
        await asyncio.sleep(0.1)
        led.off()
        await asyncio.sleep(0.1)

async def scan_networks():
    """Scan for available WiFi networks."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = wlan.scan()
    available_ssids = [net[0].decode('utf-8') for net in networks]
    return available_ssids

async def check_internet():
    """Check if the internet is available by connecting to a known server."""
    try:
        addr_info = socket.getaddrinfo("google.com", 80)
        addr = addr_info[0][-1]
        s = socket.socket()
        s.settimeout(3)
        s.connect(addr)
        s.close()
        return True
    except OSError:
        return False
    finally:
        s.close()

async def connect_wifi(led, max_retries=5):
    """Connect to WiFi using credentials from secrets."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    connected_ssid = None

    while True:
        available_ssids = await scan_networks()
        retries = 0

        while retries < max_retries:
            led_task = asyncio.create_task(flash_led_slow(led))
            
            try:
                for ssid in available_ssids:
                    for credential in WIFI_CREDENTIALS:
                        if credential["SSID"] == ssid:
                            wlan.connect(credential["SSID"], credential["PASSWORD"])
                            while not wlan.isconnected():
                                print(f"Connecting to {ssid}...")
                                await asyncio.sleep(1)
                            if await check_internet():
                                connected_ssid = ssid
                                print(f'Connected to {credential["SSID"]}')
                                print(f'Network config: {wlan.ifconfig()}')
                                led_task.cancel()
                                try:
                                    await led_task
                                except asyncio.CancelledError:
                                    pass
                                await flash_led_fast(led, 5)
                                print(f'Connected to {credential["SSID"]} and internet is available.')
                                return connected_ssid
                            else:
                                wlan.disconnect()
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            finally:
                led_task.cancel()
                try:
                    await led_task
                except asyncio.CancelledError:
                    pass

        print("Failed to connect to WiFi after multiple attempts. Waiting before retrying...")
        await asyncio.sleep(600)  # Wait for 10 minutes before retrying
        machine.reset()

async def wifi_cleanup(wlan, led):
    """Cleanup WiFi connection and deactivate WLAN interface."""
    try:
        if wlan.isconnected():
            wlan.disconnect()
            print("Disconnected from WiFi.")
        wlan.active(False)
        print("WLAN interface deactivated.")
        led.off()
        print("LED turned off.")
    except Exception as e:
        print(f"An error occurred during WiFi cleanup: {e}")
    finally:
        print("WiFi and LED cleanup completed.")


# Main function to run the asyncio loop
async def main():
    led = machine.Pin("LED", machine.Pin.OUT)
    wlan = network.WLAN(network.STA_IF)
    try:
        connected_ssid = await connect_wifi(led)
        if not connected_ssid:
            print("Internet check failed. Resetting device...")
            machine.reset()
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the main function
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user. Cleaning up...")
        wlan = network.WLAN(network.STA_IF)
        led = machine.Pin("LED", machine.Pin.OUT)
        asyncio.run(wifi_cleanup(wlan, led))
        print("Cleanup complete. Exiting...")