class helpFunctions:
    def __init__(self):
        pass

    def all_values_non_zero(self,data):
            '''
            Check if all values in the data are non-zero.
            '''
            if all(value == 0 for value in data.values()):
                return False
            return True
    def check_status(self,status):
            """
            Evaluate the platform's status based on LiDAR sensor input values.
            Parameters:
                status (dict): A dictionary containing the current status information of the platform.
            Returns:
                int: Represents the operational status of the platform as determined by sensor data.
                    - stop = 0
                    - drive = 1
                    - decrease = 2
                    - unknown = -1
            """
            if any(value == 0 for value in status.values()):
                return 0
            elif all(value == 1 for value in status.values()):
                return 1
            elif any(value == 2 for value in status.values()):
                return 2
            else:
                return -1
    def check_error(self,cluster):
            '''
            Corrects zero and extremely high values in a list of key-value pairs.
            It corrects any values that are zero or out of the LiDAR Scan Range  
            by replacing them with the average of non-zero values in the cluster.
        
            Parameters:
                cluster : list of lists
                A list of [key, value] pairs, where 'key' represents an identifier (angle),and 'value' is a float(distance).

            Returns:
            list of clean data - corrected_cluster
                
            '''
            sum_second_values = sum(value for _, value in cluster if value != 0)
            non_zero_count = sum(1 for _, value in cluster if value != 0)
            if non_zero_count == 0:
                avg_second_values = 0 
            else:
                avg_second_values = sum_second_values / non_zero_count
            corrected_cluster = [
                (key, round(avg_second_values, 2)) if value == 0 or value>=1000 else (key, value) 
                for key, value in cluster
            ]

            return corrected_cluster
        