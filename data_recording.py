import machine
import os
import time
import dht
import sdcard



dht_sensor_in = dht.DHT22(machine.Pin(14))  # Indoor sensor DRYER
dht_sensor_out = dht.DHT22(machine.Pin(15)) # Outdoor sensor CONTROL BOX    

adc = machine.ADC(machine.Pin(26))
V_REF = 3.3  # Reference voltage

# SD card configuration
spi = machine.SPI(0, baudrate=1000000, polarity=0, phase=0, sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))
cs = machine.Pin(5, machine.Pin.OUT)

# Mount the SD card
try:
    sd = sdcard.SDCard(spi, cs)
    #sd = machine.SDCard(spi, cs)
    os.mount(sd, "/sd")
    print("SD card mounted successfully")
except Exception as e:
    print("Error mounting SD card:", e)
    raise

# CSV file setup
csv_file = "/sd/data_log.csv"

# Write headers if file doesn't exist
if not "data_log.csv" in os.listdir("/sd"):
    with open(csv_file, "w") as file:
        file.write("Timestamp,Temperature_F,Humidity,Temperature_F2,Humidity2,Voltage\n")

# Read DHT22 function
def read_dht_values():
    try:
        # Read indoor sensor
        dht_sensor_in.measure()
        temp_in_c = dht_sensor_in.temperature()
        humidity_in = dht_sensor_in.humidity()
        temp_in_f = temp_in_c * 9 / 5 + 32

        # Read outdoor sensor
        dht_sensor_out.measure()
        temp_out_c = dht_sensor_out.temperature()
        humidity_out = dht_sensor_out.humidity()
        temp_out_f = temp_out_c * 9 / 5 + 32

        return temp_in_f, humidity_in, temp_out_f, humidity_out
    except Exception as e:
        print("Error reading DHT sensors:", e)
        return None, None, None, None

# Function to read solar cell voltage
def read_voltage():
    adc_value = adc.read_u16()
    voltage = (adc_value / 65535) * V_REF
    return voltage

# Function to record values into the CSV
def record_values(temp_f, humidity, temp_f2, humidity2, voltage):
    try:
        with open(csv_file, "a") as file:
            timestamp = time.localtime()  # Get the current time (YYYY-MM-DD HH:MM:SS format)
            formatted_time = f"{timestamp[0]}-{timestamp[1]:02d}-{timestamp[2]:02d} {timestamp[3]:02d}:{timestamp[4]:02d}:{timestamp[5]:02d}"
            file.write(f"{formatted_time},{temp_f},{humidity},{temp_f2},{humidity2},{voltage}\n")
            print(f"Recorded: {formatted_time}, {temp_f}, {humidity}, {temp_f2}, {humidity2}, {voltage}")
    except Exception as e:
        print("Error writing to file:", e)

# Main loop to log data every minute
try:
    while True:
        temp_f_in, humidity_in, temp_f_out, humidity_out = read_dht_values()
        voltage = read_voltage()

        if temp_f_in is not None and temp_f_out is not None:
            record_values(temp_f_in, humidity_in, temp_f_out, humidity_out, voltage)
        else:
            print("Skipping recording due to sensor read error.")

        time.sleep(60)
except KeyboardInterrupt:
    print("Logging stopped")

# Unmount the SD card
try:
    os.umount("/sd")
    print("SD card unmounted successfully")
except Exception as e:
    print("Error unmounting SD card:", e)
