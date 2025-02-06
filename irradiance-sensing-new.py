from machine import ADC
import time

# Initialize ADC on Pin 26
adc = ADC(26)

def read_voltage(adc_pin, reference_voltage=3.3, resolution=65535):
    raw_value = adc_pin.read_u16()  # Read the raw 16-bit ADC value
    return (raw_value / resolution) * reference_voltage

def voltage_to_irradiance(voltage, max_voltage=2.5, max_irradiance=1800):
    if voltage < 0:
        return 0
    elif voltage > max_voltage:
        return max_irradiance
    else:
        return (voltage / max_voltage) * max_irradiance

# Main loop
while True:
    voltage = read_voltage(adc)
    irradiance = voltage_to_irradiance(voltage)
    print(f"Voltage: {voltage:.2f} V, Irradiance: {irradiance:.2f} W/m²")
    time.sleep(1)
