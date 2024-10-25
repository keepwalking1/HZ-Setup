import random
import time
import threading

# Flag to signal the thread to terminate
terminate_flag = False

def sensor_fusion_thread():
    """Simulate combining readings from multiple sensors."""
    while not terminate_flag:
        # Simulate individual sensor readings
        temperature = random.uniform(20, 25)  # Temperature in °C
        humidity = random.uniform(50, 60)     # Humidity in %
        light_intensity = random.uniform(300, 500)  # Light intensity in lux

        # Calculate the fused value (e.g., average of the sensor readings)
        fused_value = (temperature + humidity + light_intensity) / 3

        # Print the fused value with individual sensor readings
        print(f"Temperature: {temperature:.2f}°C, "
              f"Humidity: {humidity:.2f}%, "
              f"Light: {light_intensity:.2f} lux, "
              f"Fused Value: {fused_value:.2f}")

        # Wait 1 second before the next reading
        time.sleep(1)

if __name__ == "__main__":
    try:
        # Start the fusion thread
        fusion_thread = threading.Thread(target=sensor_fusion_thread)
        fusion_thread.start()

        # Run the simulation for 10 seconds
        time.sleep(10)
    finally:
        # Set the termination flag and wait for the thread to stop
        terminate_flag = True
        fusion_thread.join()
        print("Fusion simulation complete.")
