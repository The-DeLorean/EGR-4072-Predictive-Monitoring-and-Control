from machine import Pin, PWM, SPI
import time
import sdcard
import os
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
stepper = StepperController(dir_pin=16, step_pin=17, enable_pin=18)
try:
    stepper.step_by_percentage(50, direction=1, delay=0.005)  # Rotate stepper motor by 50% of a full revolution
    print("Stepper motor moved 50% of a full revolution.")
finally:
    stepper.disable()
    print("Stepper motor disabled.")
    
# to run stepper you have to call the whole class and re initialize
# StepperController(dir_pin=16, step_pin=17, enable_pin=18).step_by_percentage(50,direction=1,delay=0.005)


# temperature stuff
import dht
dht_sensor_in_box = 15
dht_external = dht.DHT22(Pin(dht_sensor_in_box))
def getSensorData():
    # Trigger the DHT22 to take a reading
    dht_external.measure()
    # Read temperature and humidity from the sensor
    temperature_c_EX = dht_external.temperature()  # in Celsius
    humidity_EX = dht_external.humidity()          # in 
    #Convert Celsius to Fahrenheit
    temperature_f_EX = temperature_c_EX * 9 / 5 + 32
        # Print the values to the terminal
    return temperature_f_EX, humidity_EX

# SD card stuff
def record_values(temp_f, humidity, temp_f2, humidity2, voltage):
    try:
        with open(csv_file, "a") as file:
            timestamp = time.localtime()  # Get the current time (YYYY-MM-DD HH:MM:SS format)
            formatted_time = f"{timestamp[0]}-{timestamp[1]:02d}-{timestamp[2]:02d} {timestamp[3]:02d}:{timestamp[4]:02d}:{timestamp[5]:02d}"
            file.write(f"{formatted_time},{temp_f},{humidity},{temp_f2},{humidity2},{voltage}\n")
            print(f"Recorded: {formatted_time}, {temp_f}, {humidity}, {temp_f2}, {humidity2}, {voltage}")
    except Exception as e:
        print("Error writing to file:", e)

#initialize sd card
spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))
cs = Pin(5, machine.Pin.OUT)

sd = sdcard.SDCard(spi,cs)
os.mount(sd,"/sd")
print("SD card mounted successfully")
# CSV file setup
csv_file = "/sd/data_log.csv"

# Write headers if file doesn't exist
if not "data_log.csv" in os.listdir("/sd"):
    with open(csv_file, "w") as file:
        file.write("Timestamp,Temperature_F,Humidity,Temperature_F2,Humidity2,Voltage\n")