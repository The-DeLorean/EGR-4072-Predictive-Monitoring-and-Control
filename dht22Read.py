from machine import Pin
import time
import dht

dht_sensor = dht.DHT22(Pin(14))
#sensor inside CONTROL box
dht_sensorIn = dht.DHT22(Pin(15))
#Set this to true before calling function || Set to false to exit function
temp_reading_active = False

def temp():
    global temp_reading_active
    
    while temp_reading_active:
        try:
            # Trigger the DHT22 to take a reading
            dht_sensor.measure()
            dht_sensorIn.measure()
            # Read temperature and humidity from the sensor
            temperature_c = dht_sensor.temperature()  # in Celsius
            humidity = dht_sensor.humidity()          # in %
            
            temperature_c2 = dht_sensor.temperature()  # in Celsius
            humidity2 = dht_sensor.humidity()          # in %
            
            # Convert Celsius to Fahrenheit
            temperature_f = temperature_c * 9 / 5 + 32
            temperature_f2 = temperature_c2 * 9 / 5 + 32

            # Print the values to the terminal
            print("Temperature Out: {:.2f}°C / {:.2f}°F, Humidity: {}%".format(temperature_c, temperature_f, humidity))
            print("Temperature In: {:.2f}°C / {:.2f}°F, Humidity: {}%".format(temperature_c2, temperature_f2, humidity2))
            
        except OSError as e:
            # Handle any sensor read errors
            print("Failed to read sensor:", e)
            
        # Wait for 2 seconds before taking another reading
        time.sleep(2)

temp()

