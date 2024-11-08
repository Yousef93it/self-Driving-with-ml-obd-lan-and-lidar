from pyrplidar import PyRPlidar
import os
import json
from Log import logFile
import time

class Lidar:
    """
    Class to handle the RPLidar A1M8 sensor.
    
    """
    # Lidar connection parameters
    PORT_NAME = '/dev/ttyUSB0'
    RATE = 115200
    TIMEOUT = 3

    def __init__(self, path):
        """
        Initializes the Lidar class with:
        - lidar: Instance of PyRPlidar.
        - log: Log object for recording sensor activity.
        - scan_count: Counter for the number of scans to trigger data writing.
        - distance_data: Dictionary to store distance data for each angle.
        - batch_size: Number of scans to perform before writing data.
        - path: Path to store data files.
        - connect: Boolean state to check lidar connection status.
        """
        self.lidar = PyRPlidar()
        self.log = logFile(os.path.join(path, 'selfDrivingD/log/lidar_logs.log'))
        self.scan_count = 0
        self.distance_data = {angle: 0 for angle in range(360)}
        self.batch_size = 360
        self.path = path
        self.connect = False

    def create_scan_data_2d_array(self, scan_data):
        """
        Fills the 2D distance array with scan data.
        Each scan data entry is a list with angle and distance as elements.
        Updates distance data only if the new reading differs.
        """
        angle, distance = int(scan_data[0]), int(scan_data[1])
        if angle in self.distance_data and distance >= 0:
            self.distance_data[angle] = distance / 10  # Convert distance to cm from mm 

    def set_lidar_state(self, connect):
        """
        Sets the lidar connection state.
        """
        self.connect = connect

    def get_lidar_state(self):
        """
        Returns the current connection state of the lidar.
        """
        return self.connect

    def write_to_json(self, data):
        """
        Writes scan data to a JSON file at a specified path.
        """
        if not self.connect:
            self.set_lidar_state(True)
            print("Lidar connected and writing to JSON file.")

        json_path = os.path.join(self.path, 'data/lidarData.json')
        with open(json_path, 'w') as dataLiDAR:
            json.dump(data, dataLiDAR, indent=4)

    def get_scan_data(self):
        """
        Returns the current scan data dictionary.
        """
        return self.distance_data

    def run(self):
        """
        Runs the lidar sensor, records distance data, and logs information.
        Connects to the sensor and starts data collection, writing JSON periodically.
        """
        while True:
            try:
                self.lidar.connect(port=self.PORT_NAME, baudrate=self.RATE, timeout=self.TIMEOUT)
                self.log.log(f"Lidar info: {self.lidar.get_info()}")
                self.log.log(f"Lidar health: {self.lidar.get_health()}")
                
                self.lidar.set_motor_pwm(1000)
                scan_generator = self.lidar.start_scan_express(0)
                self.log.log('Recording measurements...')

                scan_count = 0
                for _, scan in enumerate(scan_generator()):
                    self.create_scan_data_2d_array([int(round(scan.angle)), int(round(scan.distance))])
                    scan_count += 1

                    # Write data if batch size reached
                    if scan_count >= self.batch_size:
                        self.write_to_json(self.distance_data)
                        scan_count = 0

            except Exception as e:
                self.log.log(f"An error occurred: {e}. Retrying in 1 second...")
                time.sleep(1)

            except KeyboardInterrupt:
                self.log.log("Lidar stopped manually.")
                break

            finally:
                # Ensure Lidar motor stops and disconnects
                self.lidar.stop()
                self.lidar.set_motor_pwm(0)
                self.lidar.disconnect()
                self.log.log("Lidar disconnected.")

if __name__ == '__main__':
    pass
