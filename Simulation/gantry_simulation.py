import time
import csv
from datetime import datetime
from unittest import mock  # Use mock for simulation
import signal
import sys

# Mock GPIO and camera modules
GPIO = mock.MagicMock()
picamera = mock.MagicMock()

# Initialize mock sensors
mock_dht22 = mock.MagicMock()
mock_bh1750 = mock.MagicMock()
mock_mlx90614 = mock.MagicMock()

# Simulate sensor values changing dynamically
def update_mock_sensors():
    """Simulate sensor values updating over time."""
    mock_dht22.temperature += 0.1  # Increment temperature slightly
    mock_dht22.humidity += 0.2     # Increment humidity slightly
    mock_bh1750.lux += 5.0         # Increase light intensity

# Assign initial sensor values
mock_dht22.temperature = 24.0
mock_dht22.humidity = 50.0
mock_bh1750.lux = 400.0
mock_mlx90614.ambient_temperature = 22.5
mock_mlx90614.object_temperature = 27.0

GPIO.input = mock.MagicMock(return_value=1)  # Simulate soil moisture (wet)
camera = picamera.PiCamera()

# Signal handler for graceful termination
def signal_handler(signal_received, frame):
    print("Interrupt received! Cleaning up...")
    sys.exit(0)

# Register the signal handler for interrupt signals (e.g., Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def read_sensors():
    """Read sensors and update mock values."""
    try:
        update_mock_sensors()  # Simulate sensor value changes over time

        temperature = mock_dht22.temperature
        humidity = mock_dht22.humidity
        light_intensity = mock_bh1750.lux
        ambient_temp = mock_mlx90614.ambient_temperature
        object_temp = mock_mlx90614.object_temperature
        soil_moisture = GPIO.input(17)
        distance = 100.0  # Mocked distance value in cm

        # Return all sensor data
        return [
            temperature, humidity, light_intensity,
            ambient_temp, object_temp, soil_moisture, distance
        ]

    except RuntimeError as e:
        print(f"Sensor read error: {e}")
        return None

def log_data_to_csv(file, data):
    """Log data to CSV with precise timestamps."""
    writer = csv.writer(file)
    writer.writerow(data)
    file.flush()  # Ensure the data is immediately written to disk

def capture_image(image_id):
    """Simulate capturing an image."""
    image_filename = f'image_{image_id:04d}.jpg'
    print(f"Simulated image captured: {image_filename}")
    return image_filename

def run_gantry_simulation(duration=10, csv_filename='sensor_log.csv'):
    """Run the gantry system and log sensor data in real-time."""
    start_time = time.time()
    image_counter = 1

    # Open the CSV file with minimal buffering
    with open(csv_filename, mode='w', newline='', buffering=1) as file:
        writer = csv.writer(file)
        writer.writerow([
            "Timestamp", "Temperature", "Humidity", "Light Intensity",
            "Ambient Temp", "Object Temp", "Soil Moisture",
            "Ultrasound Distance", "Image File"
        ])

        # Continuously collect and log data
        while time.time() - start_time < duration:
            # Capture the timestamp right before reading sensors
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Millisecond precision

            # Read sensors and capture dynamic data
            sensor_data = read_sensors()

            if sensor_data:
                # Capture an image for every reading
                image_file = capture_image(image_counter)
                image_counter += 1

                # Log the sensor data with timestamp and image filename
                log_data_to_csv(file, [timestamp] + sensor_data + [image_file])

            time.sleep(0.5)  # Adjust interval to 0.5 seconds for finer data capture

if __name__ == "__main__":
    try:
        run_gantry_simulation(duration=5)  # Run for 5 seconds
    finally:
        print("Simulation complete.")
