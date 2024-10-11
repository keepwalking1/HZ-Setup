import time
import board
import busio
import adafruit_dht
import adafruit_bh1750  # For BH1750 light intensity sensor
import adafruit_mlx90614  # For MLX90614 infrared temperature sensor
import csv
import RPi.GPIO as GPIO

# Initialize I2C bus

'''
 I2C is ideal in this case because:

Simplicity: I2C only requires two data lines (SDA and SCL) for communication between the microcontroller and multiple sensors, reducing the number of GPIO pins required.

Multi-device support: We can easily connect multiple I2C devices to the same bus by assigning different addresses to each sensor.

Synchronized communication: I2C allows all connected devices to share the same clock, which simplifies timing synchronization between sensors.
'''
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize sensors

# The DHT22 uses a dedicated GPIO pin (in this case, GPIO 4) for temperature and humidity readings.
dht22 = adafruit_dht.DHT22(board.D4)  # GPIO pin D4 for DHT22 sensor
bh1750 = adafruit_bh1750.BH1750(i2c)  # Light intensity sensor on I2C
mlx90614 = adafruit_mlx90614.MLX90614(i2c)  # IR temp sensor on I2C

# GPIO setup for capacitive soil moisture sensor and ultrasound sensor
soil_moisture_pin = 17  # could replace using real GPIO pin

# The ultrasound sensor uses two GPIO pins: one for the trigger and another for the echo. 
ultrasound_pin_trigger = 18  # Trigger pin for ultrasound sensor
ultrasound_pin_echo = 27  # Echo pin for ultrasound sensor

GPIO.setmode(GPIO.BCM)
GPIO.setup(soil_moisture_pin, GPIO.IN)
GPIO.setup(ultrasound_pin_trigger, GPIO.OUT)
GPIO.setup(ultrasound_pin_echo, GPIO.IN)

# Function to measure soil moisture (binary sensor: wet/dry)
def read_soil_moisture():
    return GPIO.input(soil_moisture_pin)

# Function to measure distance (ultrasound sensor for insect detection)
def read_ultrasound_distance():
    GPIO.output(ultrasound_pin_trigger, True)
    time.sleep(0.00001)
    GPIO.output(ultrasound_pin_trigger, False)
    
    start_time = time.time()
    stop_time = time.time()
    
    while GPIO.input(ultrasound_pin_echo) == 0:
        start_time = time.time()
    
    while GPIO.input(ultrasound_pin_echo) == 1:
        stop_time = time.time()
    
    # Calculate distance based on the time difference
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2  # Speed of sound: 34300 cm/s
    return distance

# Main function to read sensors
def read_sensors():
    try:
        # Read temperature and humidity from DHT22
        temperature = dht22.temperature
        humidity = dht22.humidity
        
        # Read light intensity from BH1750
        light_intensity = bh1750.lux
        
        # Read infrared temperature from MLX90614
        ambient_temp = mlx90614.ambient_temperature
        object_temp = mlx90614.object_temperature
        
        # Read soil moisture
        soil_moisture = read_soil_moisture()
        
        # Read ultrasound distance (for pest detection)
        distance = read_ultrasound_distance()
        
        # Print sensor data 
        print(f"Temperature: {temperature:.2f}°C, Humidity: {humidity:.2f}%")
        print(f"Light Intensity: {light_intensity:.2f} lux")
        print(f"Ambient Temp (IR): {ambient_temp:.2f}°C, Object Temp: {object_temp:.2f}°C")
        print(f"Soil Moisture: {'Wet' if soil_moisture == 1 else 'Dry'}")
        print(f"Ultrasound Distance: {distance:.2f} cm")

        return [temperature, humidity, light_intensity, ambient_temp, object_temp, soil_moisture, distance]

    except RuntimeError as error:
        print(f"Sensor reading error: {error}")
        return None

# Function to log sensor data to CSV
def log_sensor_data_to_csv(filename, duration=60):
    start_time = time.time()

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Temperature", "Humidity", "Light Intensity", "Ambient Temp", "Object Temp", "Soil Moisture", "Ultrasound Distance"])
        
        while time.time() - start_time < duration:
            sensor_data = read_sensors()
            if sensor_data:
                # Add timestamp to the sensor data
                timestamp = time.time()
                writer.writerow([timestamp] + sensor_data)

            time.sleep(1)  # Read sensors every 1 second

# Run the sensor reading and logging function for 60 seconds
if __name__ == "__main__":
    log_sensor_data_to_csv('sensor_data_log.csv', duration=60)

# Cleanup GPIO after execution
GPIO.cleanup()
