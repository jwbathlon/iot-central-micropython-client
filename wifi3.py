import network
import uasyncio as asyncio
from secrets import WIFI_CREDENTIALS
import machine
import urequests

# Initialize the LED pin
led = machine.Pin("LED", machine.Pin.OUT)
led_flash_slow = True

async def check_internet():
    try:
        await asyncio.sleep(2)
        response = urequests.get('http://www.google.com')
        if response.status_code == 200:
            return True
    except:
        return False
    return False

async def flash_led_slow():
    global led_flash_slow
    while led_flash_slow:
        led.on()
        await asyncio.sleep(1)
        led.off()
        await asyncio.sleep(1)

async def flash_led_fast(times):
    for _ in range(times):
        led.on()
        await asyncio.sleep(0.1)
        led.off()
        await asyncio.sleep(0.1)

async def scan_networks():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = wlan.scan()
    available_ssids = [net[0].decode('utf-8') for net in networks]
    return available_ssids

async def connect_wifi():
    global led_flash_slow
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    connected_ssid = None
    
    while True:
        available_ssids = await scan_networks()
        led_flash_slow = True
        led_task = asyncio.create_task(flash_led_slow())
        
        for ssid in available_ssids:
            for credential in WIFI_CREDENTIALS:
                if credential["SSID"] == ssid:
                    wlan.connect(credential["SSID"], credential["PASSWORD"])
                    while not wlan.isconnected():
                        print(f'Connecting to {credential["SSID"]}...')
                        await asyncio.sleep(3)
                    connected_ssid = credential["SSID"]
                    print(f'Connected to {credential["SSID"]}')
                    print('Network config:', wlan.ifconfig())

                    if await check_internet():
                        print(f'Connected to {credential["SSID"]} and internet is available.')
                        led_flash_slow = False
                        await flash_led_fast(5)
                        return
                    else:
                        print(f'Connected to {credential["SSID"]} but no internet. Retrying...')
                        wlan.disconnect()
                        await asyncio.sleep(300)  # Wait for 5 minutes before retrying
                        machine.reset()  # Reset the device

        print('No known networks found. Retrying in 5 minutes...')
        led_flash_slow = False
        await asyncio.sleep(300)  # Wait for 5 minutes before retrying
    
async def wifi_cleanup():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        wlan.disconnect()
        print('Disconnected from WiFi')
    wlan.active(False)
    print('WLAN interface deactivated')

async def main():
     await connect_wifi()


if __name__ == "__main__":
    try:
        # Run the main function
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"Unhandled exception in main: {e}")
        print("Resetting device...")
        machine.reset()  # Reset the device
   # finally:
        # Ensure cleanup is called before exiting
     #   asyncio.run(wifi_cleanup())
     #   print("WiFi cleanup complete")



        
