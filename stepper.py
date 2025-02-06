from machine import Pin
import time

def stepper(percent):
    # Define pins for the A4988 driver
    DIR_PIN = 16   # Direction pin
    STEP_PIN = 17  # STEP pin
    ENABLE_PIN = 18  # Enable pin (optional)

    # Set up the pins
    step_pin = Pin(STEP_PIN, Pin.OUT)
    dir_pin = Pin(DIR_PIN, Pin.OUT)
    enable_pin = Pin(ENABLE_PIN, Pin.OUT)

    # Enable the driver (LOW is active for A4988 enable pin)
    enable_pin.value(0)

    # Total steps per full revolution
    STEPS_PER_REV = 200

    def step_motor_by_percentage(percentage, direction, delay=0.005):
        
        # Calculate the steps for the given percentage
        steps = int(STEPS_PER_REV * (percentage / 100))
        
        # Set the direction
        dir_pin.value(direction)
        
        # Loop to send pulses
        for _ in range(steps):
            # Generate pulse for step
            step_pin.value(1)
            time.sleep(delay)
            step_pin.value(0)
            time.sleep(delay)

    # Example usage:
    try:
        step_motor_by_percentage(percent, direction=1, delay=0.005)

    finally:
        # Disable the driver (set ENABLE high to turn off motor)
        enable_pin.value(1)
        
stepper(50)

