import machine

def get_cpu_temperature():
    sensor_temp = machine.ADC(4)  # Temperature sensor is on ADC channel 4
    conversion_factor = 3.3 / (65535)
    
    # Read the sensor and calculate the temperature
    reading = sensor_temp.read_u16() * conversion_factor
    
    # The temperature sensor measures the Vbe voltage of a biased bipolar diode, connected to the fifth ADC channel
    # Typically, the temperature can be calculated using the formula from the RP2040 datasheet
    temperature = 27 - (reading - 0.706)/0.001721
    return temperature

# Example usage
#temp = get_cpu_temperature()
#print("CPU Temperature:", temp, "°C")