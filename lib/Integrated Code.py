# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 13:12:33 2024

@author: Paulh
"""

import math
from machine import Pin, PWM, ADC, SPI
#import machine
import time
import dht
import sdcard
import os

#Pins 
Fan_PWM = 0
SD_SCK_Clock = 2
SD_Master_Out_Slave_In = 3
SD_Master_Out_Slave_Out = 4
SD_Chip_Select = 5
DHT_Dryer = 14
DHT_Inside_Box = 15
Stepper_Direction = 16
Stepper_Step = 17
Irradiance_Signal_Neg = 26
Irradiance_Signal_Pos = 27
Solar_Panel_Pos = 28

UI_CLK_Hardware_SPIO = 9
UI_Data = 10
UI_DC = 11
UI_Rst = 12
UI_CS = 14
UI_Operate_Current = 21
UI_Select_Previous = 24
Ui_Select_Next = 25

# Start up
dht_external = dht.DHT22(Pin(15))
dht_internal = dht.DHT22(Pin(14))
adc = ADC(Pin(28)) # solar cell

step_pin = Pin(Stepper_Step,Pin.OUT)
dir_pin = Pin(Stepper_Direction,Pin.OUT)

spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))
cs = Pin(5, machine.Pin.OUT)

fan_pin = Pin(15, Pin.OUT)
pwm = PWM(fan_pin)
pwm.freq(25000)

irradianceDevice = ADC(Irradiance_Signal_Neg)
v_ref = 3.3
#Pyranometer specifications
i_min = 4    # Minimum current (mA)
i_max = 20   # Maximum current (mA)
irradiance_range = 1800
resistor = 220


#Functions
# Turn motor a certain amount
def step_motor_by_percentage(percentage, direction, delay): # percentage (1-100), direction (1-0)
    # Total steps per full revolution
    STEPS_PER_REV = 200
        # Calculate the steps for the given percentage
    steps = int(STEPS_PER_REV * (percentage / 100))
        # Set the direction
    dir_pin.value(direction)
    
    print(f"Steps: {steps}, Direction: {direction}, Delay: {delay}")
        # Loop to send pulses
    for _ in range(steps):
         # Generate pulse for step
        step_pin.value(1)
        time.sleep(delay)
        step_pin.value(0)
        time.sleep(delay)
        #time.sleep(.01)

def set_fan_speed(duty_cycle_percent):
    # Convert percentage to duty cycle (0-65535 scale for duty_u16)
    duty = int(duty_cycle_percent * 65535 / 100)
    pwm.duty_u16(duty)

def getSensorData():
    # Trigger the DHT22 to take a reading
    dht_external.measure()
    dht_internal.measure()
    # Read temperature and humidity from the sensor
    temperature_c_EX = dht_external.temperature()  # in Celsius
    humidity_EX = dht_external.humidity()          # in 
    temperature_c_IN = dht_internal.temperature()  # in Celsius
    humidity_IN = dht_internal.humidity()          # in %
    #Convert Celsius to Fahrenheit
    temperature_f_EX = temperature_c_EX * 9 / 5 + 32
    temperature_f_IN = temperature_c_IN * 9 / 5 + 32
        # Print the values to the terminal
    #print("Temperature Out: {:.2f}°C / {:.2f}°F, Humidity: {}%".format(temperature_c, temperature_f, humidity))
    #print("Temperature In: {:.2f}°C / {:.2f}°F, Humidity: {}%".format(temperature_c2, temperature_f2, humidity2))
    return temperature_f_EX, temperature_f_IN, humidity_EX,humidity_IN

# Gets irradiance
def getSolarPanel():
    ADC_converter = 65535
    max_irradiance = 2000
    min_voltage = 0.66
    max_voltage = 3.3
    
    ADC_value = adc.read_u16()
    voltage = ADC_value * (max_voltage / ADC_converter)
    irradiance = (voltage - min_voltage) * (max_irradiance / (max_voltage - min_voltage))
    #print("Solar Panel:", irradiance, "W/m²")   
    return irradiance

def getIrradiance():
    adc_value = irradianceDevice.read_u16()
    v_measured = (adc_value / 65535) * v_ref

    # Convert voltage to irradiance (W/m²)
    irradiance = ((v_measured / resistor) * 1000 - i_min) * (irradiance_range / (i_max - i_min))

    return irradiance
def record_values(temp_f, humidity, temp_f2, humidity2, voltage):
    try:
        with open(csv_file, "a") as file:
            timestamp = time.localtime()  # Get the current time (YYYY-MM-DD HH:MM:SS format)
            formatted_time = f"{timestamp[0]}-{timestamp[1]:02d}-{timestamp[2]:02d} {timestamp[3]:02d}:{timestamp[4]:02d}:{timestamp[5]:02d}"
            file.write(f"{formatted_time},{temp_f},{humidity},{temp_f2},{humidity2},{voltage}\n")
            print(f"Recorded: {formatted_time}, {temp_f}, {humidity}, {temp_f2}, {humidity2}, {voltage}")
    except Exception as e:
        print("Error writing to file:", e)

def calculateEMC(temp, RH): # this is my temp equation, but lets use the excel sheet one
    C = 30.205
    E = 0.33872
    F = 0.05897
    log_RH = math.log(RH/100)
    tempC = (temp-32)*(5/9)
    temp_plusC = -(tempC+C)
    multiplyLnRh = temp_plusC*log_RH
    print("multiply ",multiplyLnRh)
    multiplyByF = -math.log(multiplyLnRh)*F
    EMCd = (multiplyByF+E)*100
    EMCw = (100*EMCd)/(100+EMCd)
    return EMCw;

# intitalize code: fan = max, vent = open
set_fan_speed(100)
step_motor_by_percentage(10, 1, .005)

#initialize sd card
sd = sdcard.SDCard(spi,cs)
os.mount(sd,"/sd")
print("SD card mounted successfully")
# CSV file setup
csv_file = "/sd/data_log.csv"

# Write headers if file doesn't exist
if not "data_log.csv" in os.listdir("/sd"):
    with open(csv_file, "w") as file:
        file.write("Timestamp,Temperature_F,Humidity,Temperature_F2,Humidity2,Voltage\n")

while(True):
    tempFEx, tempFIn, RHex, RHin = getSensorData()
    solar = getSolarPanel()
    irradiance = getIrradiance()
    EMC = calculateEMC(tempFIn,RHin)
    print(tempFEx," ",tempFIn," ",RHex," ",RHin," "," ",EMC)
    print("Irradiance: {:.2f} W/m²".format(irradiance))
    print("Solar Panel: ",solar)
    print()
    
    if tempFEx is not None and tempFIn is not None:
            record_values(tempFEx, RHex, tempFIn, RHin, solar)
    
    #step_motor_by_percentage(percentage, direction, delay)
    time.sleep(1)

