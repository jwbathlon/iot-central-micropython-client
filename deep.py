import machine
import time

# Set up the LED pin
led = machine.Pin(25, machine.Pin.OUT)

# Function to blink the LED
def blink_led():
    for _ in range(5):
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)

# Check the reset cause
reset_cause = machine.reset_cause()

# If the reset cause is not a deep sleep wake-up, blink the LED and go to deep sleep
if reset_cause != 0x04:  # 0x04 is the typical value for DEEPSLEEP_RESET
    blink_led()
    # Put the Pico into deep sleep for 1 minute (60000 milliseconds)
    machine.deepsleep(60000)
else:
    # After waking up, blink the LED
    blink_led()
     
#     The code is simple: it blinks the LED 5 times, then puts the Pico into deep sleep for 1 minute. After waking up, it blinks the LED again. 
#     Save the code and run it on the Pico. The LED will blink 5 times, then the Pico will go into deep sleep for 1 minute. After 1 minute, the Pico will wake up and blink the LED again. 
#     Conclusion 
#     In this tutorial, we learned how to put the Raspberry Pi Pico into deep sleep mode. We used the  machine.deepsleep()  function to put the Pjsonico into deep sleep for a specified amount of time. 
#     We also learned how to wake up the Pico from deep sleep using the  machine.reset_cause()  function. 
#     Now that you know how to put the Pico into deep sleep, you can use this feature to reduce power consumption in your projects. 
#     Thanks for reading! 
#     References 
#     Raspberry Pi Pico MicroPython Documentation
#     Related posts: 
#     How to Use the Raspberry Pi Pico ADC 
#     How to Use the Raspberry Pi Pico UART 
#     How to Use the Raspberry Pi Pico I2C 
#     How to Use the Raspberry Pi Pico SPI 
     
     
 #    Thank you for this tutorial.