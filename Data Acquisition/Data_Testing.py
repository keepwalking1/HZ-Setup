import pandas as pd
import matplotlib.pyplot as plt

# visualize the data from the CSV file
def visualize_data(filename='sensor_data.csv'):
    data = pd.read_csv(filename)
    print("Data Head:")
    print(data.head())  # Show the first few rows of data for validation

    # Plot
    plt.figure(figsize=(10, 6))
    for sensor in data.columns[1:]:  # Skip 'Timestamp'
        plt.plot(data['Timestamp'], data[sensor], label=sensor)

    plt.xlabel('Time (s)')
    plt.ylabel('Sensor Values')
    plt.title('Sensor Data Over Time')
    plt.legend()
    plt.show()

# Call the visualization function after data collection
if __name__ == "__main__":
    visualize_data('sensor_data.csv')
