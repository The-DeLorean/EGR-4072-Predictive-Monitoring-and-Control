from machine import ADC, Pin
import time

adc = ADC(Pin(26))
V_REF = 3.3

def read_voltage():
    adc_value = adc.read_u16()
    voltage = (adc_value / 65535) * V_REF 
    return voltage

while True:
    voltage = read_voltage()
    print("Voltage from solar cell:", voltage, "V")
    time.sleep(1)