import pandas as pd
import time
import serial  # using serial communication

# Self-Define sensor serial ports
SENSOR_PORTS = ['COM3', 'COM4', 'COM5']
BAUD_RATE = 9600
DATA_FILE = 'sensor_data.csv'

# Function to initialize sensor connections
def initialize_sensors():
    sensor_serials = []
    for port in SENSOR_PORTS:
        try:
            ser = serial.Serial(port, BAUD_RATE, timeout=1)
            sensor_serials.append(ser)
            print(f"Connected to sensor on {port}")
        except Exception as e:
            print(f"Error connecting to {port}: {e}")
    return sensor_serials

# Function to read from all sensors
def read_sensor_data(sensor_serials):
    sensor_readings = []
    for ser in sensor_serials:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            sensor_readings.append(data)
        else:
            sensor_readings.append('No Data')
    return sensor_readings

# Function to save sensor data to CSV
def save_to_csv(data, filename=DATA_FILE):
    columns = ['Timestamp'] + [f'Sensor_{i+1}' for i in range(len(data[0]) - 1)]
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Main data acquisition loop
def acquire_sensor_data(duration=60):
    sensor_serials = initialize_sensors()
    data_collection = []
    
    start_time = time.time()
    while time.time() - start_time < duration:
        sensor_data = read_sensor_data(sensor_serials)
        timestamp = time.time()
        data_collection.append([timestamp] + sensor_data)
        print(f"Data at {timestamp}: {sensor_data}")
        time.sleep(1)  # Adjust the sampling rate 
    
    save_to_csv(data_collection)

# Run the data acquisition process for 1 minute
acquire_sensor_data(duration=60)
