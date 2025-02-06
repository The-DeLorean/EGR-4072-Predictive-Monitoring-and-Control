# This test program controls the voltage across the fan using Low-side transistor switch that utilizes an N-Channel MOSFET 
from machine import Pin, PWM
import time

# Define the GPIO pin connected to the gate of the MOSFET
fan_pin = Pin(0, Pin.OUT)

# Set up PWM on the pin
pwm = PWM(fan_pin)

# Initialize PWM frequency to a value suitable for our fan , e.g. 25kHz
pwm.freq(25000)

# Function to set fan speed (0-100%)
def set_fan_speed(duty_cycle_percent):
    # Convert percentage to duty cycle (0-65535 scale for duty_u16)
    duty = int(duty_cycle_percent * 65535 / 100)
    pwm.duty_u16(duty)

# Example: Ramp fan speed from 0 to 100%
for duty in range(0, 100, 10):
    set_fan_speed(duty)
    print(f"Fan speed: {duty}%")
    time.sleep(0.5)

# Keep the fan running at full speed for a while
set_fan_speed(100)
time.sleep(5)

# Ramp fan speed down to 0%
for duty in range(100, 0, -10):
    set_fan_speed(duty)
    print(f"Fan speed: {duty}%")
    time.sleep(0.5)

# Turn off fan
set_fan_speed(0)
print("Fan off.")
