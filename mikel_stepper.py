from machine import Pin, PWM
import time

# Function to control the fan
class FanController:
    def __init__(self, pin, freq=25000):
        self.fan_pin = Pin(pin, Pin.OUT)
        self.pwm = PWM(self.fan_pin)
        self.pwm.freq(freq)

    def set_speed(self, duty_cycle_percent):
        # Convert percentage to duty cycle (0-65535 scale for duty_u16)
        duty = int(duty_cycle_percent * 65535 / 100)
        self.pwm.duty_u16(duty)

# Function to control the stepper motor
class StepperController:
    def __init__(self, dir_pin, step_pin, enable_pin, steps_per_rev=200):
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.enable_pin = Pin(enable_pin, Pin.OUT)
        self.steps_per_rev = steps_per_rev
        
        # Enable the driver (LOW is active for A4988 enable pin)
        self.enable_pin.value(0)

    def step_by_percentage(self, percentage, direction, delay=0.005):
        # Calculate the steps for the given percentage
        steps = int(self.steps_per_rev * (percentage / 100))
        
        # Set the direction
        self.dir_pin.value(direction)

        # Loop to send pulses
        for _ in range(steps):
            self.step_pin.value(1)
            time.sleep(delay)
            self.step_pin.value(0)
            time.sleep(delay)

    def disable(self):
        # Disable the driver (set ENABLE high to turn off motor)
        self.enable_pin.value(1)

# Initialize and control the fan
fan = FanController(pin=0)
fan.set_speed(100)  # Set fan to 100% speed
print("Fan is running at 100% speed.")

# Initialize and control the stepper motor
stepper = StepperController(dir_pin=13, step_pin=12, enable_pin=1)
try:
    stepper.step_by_percentage(15, direction=1, delay=0.005)  # Rotate stepper motor by 50% of a full revolution
    while(True):
        print()
    print("Stepper motor moved 50% of a full revolution.")
finally:
    stepper.disable()
    print("Stepper motor disabled.")

