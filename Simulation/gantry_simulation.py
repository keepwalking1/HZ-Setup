'''import time
import csv
from datetime import datetime, timezone, timedelta
from unittest import mock  # Use mock for simulation
import signal
import sys
import pytz
import json


# Mock GPIO and camera modules
GPIO = mock.MagicMock()
picamera = mock.MagicMock()

# Initialize multiple mock sensors
# DHT22 Sensors
mock_dht22_1 = mock.MagicMock()
mock_dht22_2 = mock.MagicMock()

# BH1750 Sensors
mock_bh1750_1 = mock.MagicMock()
mock_bh1750_2 = mock.MagicMock()

# MLX90614 Sensor (single instance)
mock_mlx90614 = mock.MagicMock()

# Simulate sensor values changing dynamically
failure_counter = 0  # Counter to simulate sensor failure

def update_mock_sensors():
    """Simulate sensor values updating over time."""
    global failure_counter
    failure_counter += 1

    # Simulate DHT22 sensors
    for mock_dht22 in [mock_dht22_1, mock_dht22_2]:
        if failure_counter == 5:
            # Simulate DHT22 sensor failure
            mock_dht22.temperature = None
            mock_dht22.humidity = None
        else:
            if mock_dht22.temperature is not None:
                mock_dht22.temperature += 0.1
            if mock_dht22.humidity is not None:
                mock_dht22.humidity += 0.2

    # Simulate BH1750 sensors
    for mock_bh1750 in [mock_bh1750_1, mock_bh1750_2]:
        if mock_bh1750.lux is not None:
            mock_bh1750.lux += 5.0

    # Update MLX90614 sensor
    if mock_mlx90614.ambient_temperature is not None:
        mock_mlx90614.ambient_temperature += 0.05
    if mock_mlx90614.object_temperature is not None:
        mock_mlx90614.object_temperature += 0.1

# Assign initial sensor values
# DHT22 Sensors
mock_dht22_1.temperature = 24.0
mock_dht22_1.humidity = 50.0

mock_dht22_2.temperature = 23.5
mock_dht22_2.humidity = 48.0

# BH1750 Sensors
mock_bh1750_1.lux = 400.0
mock_bh1750_2.lux = 450.0

# MLX90614 Sensor
mock_mlx90614.ambient_temperature = 22.5
mock_mlx90614.object_temperature = 27.0

# Simulate soil moisture sensor (GPIO)
GPIO.input = mock.MagicMock(return_value=1)  # Simulate soil moisture (wet)

# Initialize the camera
camera = picamera.PiCamera()

# Signal handler for graceful termination
def signal_handler(signal_received, frame):
    print("Interrupt received! Cleaning up...")
    sys.exit(0)

# Register the signal handler for interrupt signals (e.g., Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def get_formatted_timestamp():
    """Get the current timestamp formatted as '8:22 AM October 25, 2024 (CDT)'."""
    tz = pytz.timezone('America/Chicago')  # Central Time Zone
    now = datetime.now(tz)  # Get the current time in CDT

    # Use %I for the hour (12-hour clock) and strip leading zeros manually
    hour = now.strftime("%I").lstrip("0")  # Remove leading zero if present
    formatted_timestamp = f"{hour}:{now.strftime('%M %p %B %d, %Y (%Z)')}"
    
    return formatted_timestamp

def read_sensors():
    """Read sensors and update mock values."""
    # Update mock sensors to simulate changing values
    update_mock_sensors()

    # Initialize dictionaries to store sensor readings
    dht22_readings = {}
    bh1750_readings = {}

    # Read from DHT22 sensors
    for idx, mock_dht22 in enumerate([mock_dht22_1, mock_dht22_2], start=1):
        sensor_id = f'DHT22_{idx}'
        try:
            if mock_dht22.temperature is None or mock_dht22.humidity is None:
                raise RuntimeError(f"{sensor_id} sensor failure")
            dht22_readings[sensor_id] = {
                'temperature': mock_dht22.temperature,
                'humidity': mock_dht22.humidity
            }
        except RuntimeError as e:
            print(f"{sensor_id} read error: {e}")
            dht22_readings[sensor_id] = {
                'temperature': None,
                'humidity': None
            }

    # Read from BH1750 sensors
    for idx, mock_bh1750 in enumerate([mock_bh1750_1, mock_bh1750_2], start=1):
        sensor_id = f'BH1750_{idx}'
        try:
            if mock_bh1750.lux is None:
                raise RuntimeError(f"{sensor_id} sensor failure")
            bh1750_readings[sensor_id] = mock_bh1750.lux
        except RuntimeError as e:
            print(f"{sensor_id} read error: {e}")
            bh1750_readings[sensor_id] = None

    # Read temperatures from MLX90614 sensor
    try:
        if mock_mlx90614.ambient_temperature is None or mock_mlx90614.object_temperature is None:
            raise RuntimeError("MLX90614 sensor failure")
        ambient_temp = mock_mlx90614.ambient_temperature
        object_temp = mock_mlx90614.object_temperature
    except RuntimeError as e:
        print(f"MLX90614 sensor read error: {e}")
        ambient_temp = None
        object_temp = None

    # Read soil moisture from GPIO input
    try:
        soil_moisture = GPIO.input(17)
    except RuntimeError as e:
        print(f"Soil moisture sensor read error: {e}")
        soil_moisture = None

    # Read distance from ultrasonic sensor (simulated)
    try:
        distance = 100.0  # Mocked distance value in cm
    except RuntimeError as e:
        print(f"Ultrasonic sensor read error: {e}")
        distance = None

    # Combine all sensor data into a single dictionary
    sensor_data = {
        'dht22': dht22_readings,
        'bh1750': bh1750_readings,
        'ambient_temp': ambient_temp,
        'object_temp': object_temp,
        'soil_moisture': soil_moisture,
        'distance': distance
    }

    return sensor_data

def log_data_to_csv(file, data):
    """Log data to CSV with precise timestamps."""
    # Replace None values with 'N/A' 
    data = ['N/A' if d is None else d for d in data]
    writer = csv.writer(file)
    writer.writerow(data)
    file.flush()  # Ensure the data is immediately written to disk

def capture_image(image_id):
    """Simulate capturing an image."""
    image_filename = f'image_{image_id:04d}.jpg'
    print(f"Simulated image captured: {image_filename}")
    return image_filename

def run_gantry_simulation(duration=10, sensor_csv='/app/logs/sensor_log.csv', image_csv='/app/logs/image_log.csv'):
    """Run the gantry system and log sensor data and image data in real-time."""
    print(f"Writing sensor data to: {sensor_csv}")
    print(f"Writing image data to: {image_csv}")
    
    start_time = time.time()
    image_counter = 1

    # Open the sensor data CSV file and image data CSV file with minimal buffering
    with open(sensor_csv, mode='w', newline='', buffering=1) as sensor_file, \
         open(image_csv, mode='w', newline='', buffering=1) as image_file:

        # Create CSV writers for each file
        sensor_writer = csv.writer(sensor_file)
        image_writer = csv.writer(image_file)

        # Write headers for sensor data
        sensor_writer.writerow([
            "Timestamp",
            # DHT22 sensor readings
            "DHT22_1_Temperature", "DHT22_1_Humidity",
            "DHT22_2_Temperature", "DHT22_2_Humidity",
            # BH1750 sensor readings
            "BH1750_1_Lux", "BH1750_2_Lux",
            # Other sensors
            "Ambient Temp", "Object Temp",
            "Soil Moisture",
            "Ultrasound Distance"
        ])
        print("Sensor CSV headers written.")

        # Write headers for image data
        image_writer.writerow([
            "Timestamp",
            "Image File"
        ])
        print("Image CSV headers written.")

        # Continuously collect and log data
        while time.time() - start_time < duration:
            # Use the new function to get the formatted timestamp
            timestamp = get_formatted_timestamp()

            # Read sensors and capture dynamic data
            sensor_data = read_sensors()

            if sensor_data:
                # Capture an image for every reading
                image_file_name = capture_image(image_counter)
                image_counter += 1

                # Prepare the sensor data row
                sensor_data_row = [
                    timestamp,
                    # DHT22 sensor readings
                    sensor_data['dht22']['DHT22_1']['temperature'],
                    sensor_data['dht22']['DHT22_1']['humidity'],
                    sensor_data['dht22']['DHT22_2']['temperature'],
                    sensor_data['dht22']['DHT22_2']['humidity'],
                    # BH1750 sensor readings
                    sensor_data['bh1750']['BH1750_1'],
                    sensor_data['bh1750']['BH1750_2'],
                    # Other sensors
                    sensor_data['ambient_temp'],
                    sensor_data['object_temp'],
                    sensor_data['soil_moisture'],
                    sensor_data['distance']
                ]

                # Log the sensor data with timestamp
                log_data_to_csv(sensor_file, sensor_data_row)
                print(f"Logged sensor data at {timestamp}")

                # Prepare the image data row
                image_data_row = [
                    timestamp,
                    image_file_name
                ]

                # Log the image data with timestamp
                log_data_to_csv(image_file, image_data_row)
                print(f"Logged image data at {timestamp}")

            time.sleep(0.5)  # Adjust interval to 0.5 seconds for finer data capture


if __name__ == "__main__":
    try:
        run_gantry_simulation(duration=5)  # Run for 5 seconds
    finally:
        print("Simulation complete.")'''



import time
import csv
from datetime import datetime
import signal
import sys
import pytz
import json
import os

# Signal handler for graceful termination
def signal_handler(signal_received, frame):
    print("Interrupt received! Cleaning up...")
    sys.exit(0)

# Register the signal handler for interrupt signals (e.g., Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def get_formatted_timestamp():
    """Get the current timestamp formatted as '8:22 AM October 25, 2024 (CDT)'."""
    tz = pytz.timezone('America/Chicago')  # Central Time Zone
    now = datetime.now(tz)  # Get the current time in CDT

    # Use %I for the hour (12-hour clock) and strip leading zeros manually
    hour = now.strftime("%I").lstrip("0")  # Remove leading zero if present
    formatted_timestamp = f"{hour}:{now.strftime('%M %p %B %d, %Y (%Z)')}"
    
    return formatted_timestamp

def read_sensor_data(sensor_file_path):
    """Read data from a JSON file."""
    try:
        if os.path.exists(sensor_file_path):
            with open(sensor_file_path, 'r') as f:
                data = json.load(f)
                return data
        else:
            raise FileNotFoundError(f"{sensor_file_path} not found.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading sensor data: {e}")
        return None

def log_data_to_csv(file, data):
    """Log data to CSV with precise timestamps."""
    data = ['N/A' if d is None else d for d in data]
    writer = csv.writer(file)
    writer.writerow(data)
    file.flush()

def run_gantry_simulation(duration=10, sensor_csv='/app/logs/sensor_log.csv', image_csv='/app/logs/image_log.csv'):
    """Run the gantry system and log sensor data and image data in real-time."""
    print(f"Writing sensor data to: {sensor_csv}")
    print(f"Writing image data to: {image_csv}")
    
    start_time = time.time()
    image_counter = 1

    # Paths for sensor data input from Docker container
    sensor_files = [
        '/app/logs/dht22_sensor_1.json',
        '/app/logs/dht22_sensor_2.json',
        '/app/logs/bh1750_sensor_1.json',
        '/app/logs/bh1750_sensor_2.json',
        '/app/logs/mlx90614_sensor.json'
    ]

    # Open the CSV files for writing
    with open(sensor_csv, mode='w', newline='', buffering=1) as sensor_file, \
         open(image_csv, mode='w', newline='', buffering=1) as image_file:

        # Create CSV writers for each file
        sensor_writer = csv.writer(sensor_file)
        image_writer = csv.writer(image_file)

        # Write headers for sensor data
        sensor_writer.writerow([
            "Timestamp",
            "DHT22_1_Temperature", "DHT22_1_Humidity",
            "DHT22_2_Temperature", "DHT22_2_Humidity",
            "BH1750_1_Lux", "BH1750_2_Lux",
            "Ambient Temp", "Object Temp",
            "Soil Moisture",
            "Ultrasound Distance"
        ])
        print("Sensor CSV headers written.")

        # Write headers for image data
        image_writer.writerow([
            "Timestamp",
            "Image File"
        ])
        print("Image CSV headers written.")

        # Continuously collect and log data
        while time.time() - start_time < duration:
            timestamp = get_formatted_timestamp()
            sensor_data = []

            # Read data from each sensor file
            for file_path in sensor_files:
                data = read_sensor_data(file_path)
                if data:
                    sensor_data.extend(data.values())
                else:
                    sensor_data.extend([None] * len(data.values()))

            # Log data if all sensor data is available
            if sensor_data:
                sensor_data_row = [timestamp] + sensor_data
                log_data_to_csv(sensor_file, sensor_data_row)
                print(f"Logged sensor data at {timestamp}")

                # Simulate image capture
                image_file_name = f"image_{image_counter:04d}.jpg"
                image_data_row = [timestamp, image_file_name]
                log_data_to_csv(image_file, image_data_row)
                print(f"Logged image data at {timestamp}")
                image_counter += 1

            time.sleep(0.5)  # Adjust interval as needed

if __name__ == "__main__":
    try:
        run_gantry_simulation(duration=5)  # Run for 5 seconds
    finally:
        print("Simulation complete.")
