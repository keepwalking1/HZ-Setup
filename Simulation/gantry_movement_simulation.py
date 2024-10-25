import time
import threading
import random

# Global variables for gantry position and termination flag
gantry_position = 0  # Current gantry position in cm
terminate_flag = False  # Flag to stop threads

def move_gantry(new_position):
    """Simulate moving the gantry to a new position."""
    global gantry_position
    print(f"Moving gantry from {gantry_position} cm to {new_position} cm...")

    # Simulate time taken for the movement (1 second per 10 cm)
    time_to_move = abs(new_position - gantry_position) / 10
    time.sleep(time_to_move)  # Simulate movement delay

    # Update the gantry position after movement completes
    gantry_position = new_position
    print(f"Gantry reached position {gantry_position} cm")

def gantry_thread():
    """Thread to control the gantry movement."""
    while not terminate_flag:
        # Generate a random target position between 0 and 100 cm
        target_position = random.randint(0, 100)

        # Move the gantry to the target position
        move_gantry(target_position)

        # Wait for 2 seconds before the next movement
        time.sleep(2)

def run_gantry_simulation(duration=10):
    """Run the gantry movement simulation."""
    global terminate_flag

    # Start the gantry movement thread
    thread = threading.Thread(target=gantry_thread)
    thread.start()

    print(f"Running gantry simulation for {duration} seconds...")

    # Run the simulation for the specified duration
    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(1)  # Keep the main program running

    # Stop the thread and wait for it to complete
    terminate_flag = True
    thread.join()
    print("Gantry simulation complete.")

if __name__ == "__main__":
    run_gantry_simulation(duration=10)  # Run the simulation for 10 seconds
