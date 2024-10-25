import time
import threading
import random

def fast_sensor_thread():
    """Thread for simulating a fast sensor."""
    while not terminate_flag:
        print(f"Fast sensor reading: {random.uniform(100, 200):.2f}")
        time.sleep(0.5)  # Fast sensor reads every 0.5 seconds

def slow_sensor_thread():
    """Thread for simulating a slow sensor."""
    while not terminate_flag:
        print(f"Slow sensor reading: {random.uniform(20, 25):.2f}")
        time.sleep(2)  # Slow sensor reads every 2 seconds

if __name__ == "__main__":
    terminate_flag = False  # Global flag to stop the threads

    try:
        # Start threads for fast and slow sensors
        fast_thread = threading.Thread(target=fast_sensor_thread)
        slow_thread = threading.Thread(target=slow_sensor_thread)
        fast_thread.start()
        slow_thread.start()

        # Run the simulation for 10 seconds
        time.sleep(10)
    finally:
        # Signal the threads to terminate
        terminate_flag = True
        fast_thread.join()  # Wait for fast sensor thread to finish
        slow_thread.join()  # Wait for slow sensor thread to finish
        print("Simulation complete.")
