import time
import board
import busio
import adafruit_dht
import adafruit_bh1750
import adafruit_mlx90614
import RPi.GPIO as GPIO
import picamera
import csv
from datetime import datetime

# Initialize I2C bus for light sensor (BH1750) and infrared temperature sensor (MLX90614)
i2c = busio.I2C(board.SCL, board.SDA)
bh1750 = adafruit_bh1750.BH1750(i2c)
mlx90614 = adafruit_mlx90614.MLX90614(i2c)

# Initialize GPIO for DHT22 (temperature/humidity), soil moisture, and ultrasound
dht22 = adafruit_dht.DHT22(board.D4)
soil_moisture_pin = 17
ultrasound_trigger_pin = 18
ultrasound_echo_pin = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(soil_moisture_pin, GPIO.IN)
GPIO.setup(ultrasound_trigger_pin, GPIO.OUT)
GPIO.setup(ultrasound_echo_pin, GPIO.IN)

# Initialize camera(raspberry pi)
camera = picamera.PiCamera()

# Function to read soil moisture sensor (binary wet/dry)
def read_soil_moisture():
    return GPIO.input(soil_moisture_pin)

# Function to read ultrasound sensor for pest detection
def read_ultrasound_distance():
    GPIO.output(ultrasound_trigger_pin, True)
    time.sleep(0.00001)
    GPIO.output(ultrasound_trigger_pin, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ultrasound_echo_pin) == 0:
        start_time = time.time()

    while GPIO.input(ultrasound_echo_pin) == 1:
        stop_time = time.time()

    # Calculate distance based on time difference
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2  # Speed of sound: 34300 cm/s
    return distance

# Function to capture sensor data
def capture_sensors():
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

        # Read ultrasound distance for pest detection
        distance = read_ultrasound_distance()

        return [temperature, humidity, light_intensity, ambient_temp, object_temp, soil_moisture, distance]
    
    except RuntimeError as e:
        print(f"Sensor read error: {e}")
        return None

# Function to log data to CSV
def log_data_to_csv(filename, data):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

# Function to capture image
def capture_image(image_id):
    image_filename = f'image_{image_id:04d}.jpg'
    camera.capture(image_filename)
    return image_filename

# Main function to run data pipeline and log data
def run_data_pipeline(duration=60, csv_filename='sensor_image_log.csv'):
    start_time = time.time()
    image_counter = 1

    # Create CSV file and write the header
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Temperature", "Humidity", "Light Intensity", "Ambient Temp", "Object Temp", "Soil Moisture", "Ultrasound Distance", "Image File"])

    # Run data collection for specified duration
    while time.time() - start_time < duration:
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Capture sensor data
        sensor_data = capture_sensors()
        if sensor_data:
            # Capture image
            image_file = capture_image(image_counter)
            image_counter += 1

            # Log sensor data with timestamp and image filename
            log_data_to_csv(csv_filename, [timestamp] + sensor_data + [image_file])

        time.sleep(1)  # Collect data every second

# Run the data pipeline for 60 seconds , could adjust
if __name__ == "__main__":
    run_data_pipeline(duration=60)

# Cleanup GPIO pins after execution
GPIO.cleanup()
